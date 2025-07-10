from flask import Flask, render_template, jsonify, request
import asyncio
import asyncpg
import json
import datetime
import os
from collections import defaultdict, Counter
import pandas as pd
from typing import Dict, List, Any
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration - Updated to use actual database settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Password123!@localhost:5432/conjoint")
API_BASE_URL = os.getenv("API_BASE_URL", "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com")
PORT = int(os.getenv("PORT", 5001))

# For production, use Heroku database URL
# Note: The DATABASE_URL should be set via environment variable
# For local development, it defaults to localhost
# For production, it should be the Heroku DATABASE_URL

# Convert SQLAlchemy URL format to asyncpg format
def convert_database_url(url):
    """Convert SQLAlchemy URL format to asyncpg format."""
    if url.startswith("postgresql+asyncpg://"):
        # Remove the +asyncpg part and convert to asyncpg format
        return url.replace("postgresql+asyncpg://", "postgresql://")
    return url

# Use the converted database URL
ASYNC_DATABASE_URL = convert_database_url(DATABASE_URL)

# Global connection pool and event loop
pool = None
loop = None

def get_or_create_loop():
    """Get or create the event loop."""
    global loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

async def get_db_pool():
    """Get database connection pool."""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(ASYNC_DATABASE_URL, min_size=1, max_size=10)
    return pool

async def execute_query(query: str, *args) -> List[Dict]:
    """Execute a database query and return results as list of dicts."""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def run_async_query(query: str, *args) -> List[Dict]:
    """Run an async query in a sync context."""
    try:
        loop = get_or_create_loop()
        return loop.run_until_complete(execute_query(query, *args))
    except Exception as e:
        print(f"Error running query: {e}")
        return []

@app.route('/')
def dashboard():
    """Main data analysis dashboard page."""
    return render_template('data_analysis.html')

@app.route('/api/sessions-overview')
def get_sessions_overview():
    """Get overview of all sessions."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Get total sessions
        sessions = run_async_query("""
            SELECT 
                id,
                byo_config,
                utilities
            FROM sessions 
            ORDER BY id DESC
        """)
        
        # Get session completion stats
        completion_stats = run_async_query("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN EXISTS (SELECT 1 FROM screening_tasks st WHERE st.session_id = s.id) THEN 1 END) as screening_started,
                COUNT(CASE WHEN EXISTS (SELECT 1 FROM tournament_tasks tt WHERE tt.session_id = s.id) THEN 1 END) as tournament_started,
                COUNT(CASE WHEN EXISTS (
                    SELECT 1 FROM tournament_tasks tt 
                    WHERE tt.session_id = s.id AND tt.choice IS NOT NULL
                ) THEN 1 END) as tournament_completed
            FROM sessions s
        """)
        
        # Get recent sessions with details
        recent_sessions = run_async_query("""
            SELECT 
                s.id,
                s.byo_config::text,
                s.utilities::text,
                COUNT(st.id) as screening_tasks_count,
                COUNT(CASE WHEN st.response IS NOT NULL THEN 1 END) as screening_responses,
                COUNT(tt.id) as tournament_tasks_count,
                COUNT(CASE WHEN tt.choice IS NOT NULL THEN 1 END) as tournament_choices
            FROM sessions s
            LEFT JOIN screening_tasks st ON s.id = st.session_id
            LEFT JOIN tournament_tasks tt ON s.id = tt.session_id
            GROUP BY s.id, s.byo_config::text, s.utilities::text
            ORDER BY s.id DESC
            LIMIT 20
        """)
        
        return jsonify({
            'total_sessions': len(sessions),
            'completion_stats': completion_stats[0] if completion_stats else {},
            'recent_sessions': recent_sessions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session-details/<session_id>')
def get_session_details(session_id: str):
    """Get detailed information for a specific session."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Get session info
        session_info = run_async_query("""
            SELECT id, byo_config::text, utilities::text
            FROM sessions WHERE id = $1
        """, session_id)
        
        if not session_info:
            return jsonify({'error': 'Session not found'}), 404
        
        session = session_info[0]
        
        # Get screening tasks
        screening_tasks = run_async_query("""
            SELECT id, concept::text, position, response
            FROM screening_tasks 
            WHERE session_id = $1 
            ORDER BY position
        """, session_id)
        
        # Get tournament tasks
        tournament_tasks = run_async_query("""
            SELECT id, task_number, concepts::text, choice
            FROM tournament_tasks 
            WHERE session_id = $1 
            ORDER BY task_number
        """, session_id)
        
        return jsonify({
            'session': session,
            'screening_tasks': screening_tasks,
            'tournament_tasks': tournament_tasks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/design-analysis')
def get_design_analysis():
    """Analyze designs shown across all sessions."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Get all tournament concepts shown
        tournament_concepts = run_async_query("""
            SELECT 
                concept::text,
                COUNT(*) as frequency
            FROM tournament_tasks,
            json_array_elements(CASE 
                WHEN json_typeof(concepts) = 'array' THEN concepts::json 
                ELSE '[]'::json 
            END) as concept
            GROUP BY concept::text
            ORDER BY frequency DESC
        """)
        
        # Get all screening concepts shown
        screening_concepts = run_async_query("""
            SELECT 
                concept::text,
                COUNT(*) as frequency
            FROM screening_tasks
            WHERE concept IS NOT NULL
            GROUP BY concept::text
            ORDER BY frequency DESC
        """)
        
        # Get attribute level usage
        attribute_usage = run_async_query("""
            WITH concept_data AS (
                SELECT concept::text FROM screening_tasks WHERE concept IS NOT NULL
                UNION ALL
                SELECT concept::text FROM tournament_tasks,
                json_array_elements(CASE 
                    WHEN json_typeof(concepts) = 'array' THEN concepts::json 
                    ELSE '[]'::json 
                END) as concept
            ),
            attribute_levels AS (
                SELECT 
                    key as attribute,
                    value::text as level,
                    COUNT(*) as frequency
                FROM concept_data,
                json_each(CASE 
                    WHEN json_typeof(concept::json) = 'object' THEN concept::json 
                    ELSE '{}'::json 
                END) as kv(key, value)
                GROUP BY key, value::text
            )
            SELECT attribute, level, frequency
            FROM attribute_levels
            ORDER BY attribute, frequency DESC
        """)
        
        # Concept preference analysis
        concept_preferences = run_async_query("""
            WITH concept_responses AS (
                SELECT 
                    concept::text,
                    choice,
                    COUNT(*) as frequency
                FROM tournament_tasks,
                json_array_elements(CASE 
                    WHEN json_typeof(concepts) = 'array' THEN concepts::json 
                    ELSE '[]'::json 
                END) as concept
                WHERE choice IS NOT NULL
                GROUP BY concept::text, choice
            )
            SELECT 
                concept,
                choice,
                frequency,
                ROUND(frequency * 100.0 / SUM(frequency) OVER (PARTITION BY concept), 2) as preference_percentage
            FROM concept_responses
            ORDER BY concept, frequency DESC
        """)
        
        return jsonify({
            'screening_concepts': screening_concepts,
            'tournament_concepts': tournament_concepts,
            'attribute_usage': attribute_usage
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/response-analysis')
def get_response_analysis():
    """Analyze respondent responses and choices."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Screening response analysis
        screening_responses = run_async_query("""
            SELECT 
                response,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM screening_tasks WHERE response IS NOT NULL), 2) as percentage
            FROM screening_tasks 
            WHERE response IS NOT NULL
            GROUP BY response
        """)
        
        # Tournament choice analysis
        tournament_choices = run_async_query("""
            SELECT 
                choice,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tournament_tasks WHERE choice IS NOT NULL), 2) as percentage
            FROM tournament_tasks 
            WHERE choice IS NOT NULL
            GROUP BY choice
            ORDER BY choice
        """)
        
        # Concept preference analysis
        concept_preferences = run_async_query("""
            WITH concept_responses AS (
                SELECT 
                    concept::text,
                    choice,
                    COUNT(*) as frequency
                FROM tournament_tasks,
                json_array_elements(CASE 
                    WHEN json_typeof(concepts) = 'array' THEN concepts::json 
                    ELSE '[]'::json 
                END) as concept
                WHERE choice IS NOT NULL
                GROUP BY concept::text, choice
            )
            SELECT 
                concept,
                choice,
                frequency,
                ROUND(frequency * 100.0 / SUM(frequency) OVER (PARTITION BY concept), 2) as preference_percentage
            FROM concept_responses
            ORDER BY concept, frequency DESC
        """)
        
        return jsonify({
            'screening_responses': screening_responses,
            'tournament_choices': tournament_choices,
            'concept_preferences': concept_preferences
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/completion-analysis')
def get_completion_analysis():
    """Analyze completion rates and session flow."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Session completion flow
        completion_flow = run_async_query("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN EXISTS (SELECT 1 FROM screening_tasks st WHERE st.session_id = s.id) THEN 1 END) as screening_started,
                COUNT(CASE WHEN EXISTS (
                    SELECT 1 FROM screening_tasks st 
                    WHERE st.session_id = s.id AND st.response IS NOT NULL
                ) THEN 1 END) as screening_completed,
                COUNT(CASE WHEN EXISTS (SELECT 1 FROM tournament_tasks tt WHERE tt.session_id = s.id) THEN 1 END) as tournament_started,
                COUNT(CASE WHEN EXISTS (
                    SELECT 1 FROM tournament_tasks tt 
                    WHERE tt.session_id = s.id AND tt.choice IS NOT NULL
                ) THEN 1 END) as tournament_completed
            FROM sessions s
        """)
        
        # Since there's no created_at column, we'll use session ID for ordering
        # and provide basic session statistics instead of time-based analysis
        session_stats = run_async_query("""
            SELECT 
                s.id,
                COUNT(st.id) as screening_tasks_count,
                COUNT(CASE WHEN st.response IS NOT NULL THEN 1 END) as screening_responses,
                COUNT(tt.id) as tournament_tasks_count,
                COUNT(CASE WHEN tt.choice IS NOT NULL THEN 1 END) as tournament_choices
            FROM sessions s
            LEFT JOIN screening_tasks st ON s.id = st.session_id
            LEFT JOIN tournament_tasks tt ON s.id = tt.session_id
            GROUP BY s.id
            ORDER BY s.id DESC
            LIMIT 30
        """)
        
        # Average responses per session
        avg_responses = run_async_query("""
            SELECT 
                AVG(screening_count) as avg_screening_responses,
                AVG(tournament_count) as avg_tournament_choices,
                AVG(total_responses) as avg_total_responses
            FROM (
                SELECT 
                    s.id,
                    COUNT(CASE WHEN st.response IS NOT NULL THEN 1 END) as screening_count,
                    COUNT(CASE WHEN tt.choice IS NOT NULL THEN 1 END) as tournament_count,
                    COUNT(CASE WHEN st.response IS NOT NULL THEN 1 END) + 
                    COUNT(CASE WHEN tt.choice IS NOT NULL THEN 1 END) as total_responses
                FROM sessions s
                LEFT JOIN screening_tasks st ON s.id = st.session_id
                LEFT JOIN tournament_tasks tt ON s.id = tt.session_id
                GROUP BY s.id
            ) session_stats
        """)
        
        return jsonify({
            'completion_flow': completion_flow[0] if completion_flow else {},
            'session_stats': session_stats,  # Instead of time_analysis
            'avg_responses': avg_responses[0] if avg_responses else {}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attribute-analysis')
def get_attribute_analysis():
    """Analyze attribute preferences and utilities."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Get all BYO configurations
        byo_configs = run_async_query("""
            SELECT byo_config::text, COUNT(*) as frequency
            FROM sessions 
            GROUP BY byo_config::text
            ORDER BY frequency DESC
        """)
        
        # Analyze attribute importance from utilities
        utility_analysis = run_async_query("""
            SELECT 
                utilities::text,
                COUNT(*) as frequency
            FROM sessions 
            WHERE utilities IS NOT NULL
            GROUP BY utilities::text
            ORDER BY frequency DESC
        """)
        
        # Attribute level preference analysis
        level_preferences = run_async_query("""
            WITH concept_responses AS (
                SELECT 
                    concept::text,
                    choice,
                    COUNT(*) as frequency
                FROM tournament_tasks,
                json_array_elements(CASE 
                    WHEN json_typeof(concepts) = 'array' THEN concepts::json 
                    ELSE '[]'::json 
                END) as concept
                WHERE choice IS NOT NULL
                GROUP BY concept::text, choice
            ),
            attribute_levels AS (
                SELECT 
                    key as attribute,
                    value::text as level,
                    SUM(frequency) as total_frequency
                FROM concept_responses,
                json_each(CASE 
                    WHEN json_typeof(concept::json) = 'object' THEN concept::json 
                    ELSE '{}'::json 
                END) as kv(key, value)
                GROUP BY key, value::text
            )
            SELECT 
                attribute,
                level,
                total_frequency,
                ROUND(total_frequency * 100.0 / SUM(total_frequency) OVER (PARTITION BY attribute), 2) as preference_percentage
            FROM attribute_levels
            ORDER BY attribute, total_frequency DESC
        """)
        
        return jsonify({
            'byo_configs': byo_configs,
            'utility_analysis': utility_analysis,
            'level_preferences': level_preferences
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-data')
def export_data():
    """Export all data for analysis."""
    try:
        # Run async function in sync context
        loop = get_or_create_loop()
        
        # Get all sessions with their data
        sessions_data = run_async_query("""
            SELECT 
                s.id,
                s.byo_config::text,
                s.utilities::text,
                json_agg(
                    json_build_object(
                        'task_id', st.id,
                        'position', st.position,
                        'concept', st.concept::text,
                        'response', st.response
                    ) ORDER BY st.position
                ) as screening_tasks,
                json_agg(
                    json_build_object(
                        'task_id', tt.id,
                        'task_number', tt.task_number,
                        'concepts', tt.concepts::text,
                        'choice', tt.choice
                    ) ORDER BY tt.task_number
                ) as tournament_tasks
            FROM sessions s
            LEFT JOIN screening_tasks st ON s.id = st.session_id
            LEFT JOIN tournament_tasks tt ON s.id = tt.session_id
            GROUP BY s.id, s.byo_config::text, s.utilities::text
            ORDER BY s.id DESC
        """)
        
        return jsonify({
            'export_timestamp': datetime.datetime.now().isoformat(),
            'total_sessions': len(sessions_data),
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)

# Wrap Flask app for ASGI compatibility
asgi_app = WsgiToAsgi(app) 