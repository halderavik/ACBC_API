from flask import Flask, render_template, jsonify, request
import asyncio
import asyncpg
import json
import datetime
import os
from collections import defaultdict, Counter
import pandas as pd
from typing import Dict, List, Any

app = Flask(__name__)

# Configuration - Updated to use actual database settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:Password123!@localhost:5432/conjoint")
API_BASE_URL = os.getenv("API_BASE_URL", "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com")
PORT = int(os.getenv("PORT", 5001))

# Convert SQLAlchemy URL format to asyncpg format
def convert_database_url(url):
    """Convert SQLAlchemy URL format to asyncpg format."""
    if url.startswith("postgresql+asyncpg://"):
        # Remove the +asyncpg part and convert to asyncpg format
        return url.replace("postgresql+asyncpg://", "postgresql://")
    return url

# Use the converted database URL
ASYNC_DATABASE_URL = convert_database_url(DATABASE_URL)

# Database connection pool
pool = None

async def get_db_pool():
    """Get database connection pool."""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(ASYNC_DATABASE_URL)
    return pool

async def execute_query(query: str, *args) -> List[Dict]:
    """Execute a database query and return results as list of dicts."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]

@app.route('/')
def dashboard():
    """Main data analysis dashboard page."""
    return render_template('data_analysis.html')

@app.route('/api/sessions-overview')
async def get_sessions_overview():
    """Get overview of all sessions."""
    try:
        # Get total sessions
        sessions = await execute_query("""
            SELECT 
                id,
                byo_config,
                utilities
            FROM sessions 
            ORDER BY id DESC
        """)
        
        # Get session completion stats
        completion_stats = await execute_query("""
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
        recent_sessions = await execute_query("""
            SELECT 
                s.id,
                s.byo_config,
                s.utilities,
                COUNT(st.id) as screening_tasks_count,
                COUNT(CASE WHEN st.response IS NOT NULL THEN 1 END) as screening_responses,
                COUNT(tt.id) as tournament_tasks_count,
                COUNT(CASE WHEN tt.choice IS NOT NULL THEN 1 END) as tournament_choices
            FROM sessions s
            LEFT JOIN screening_tasks st ON s.id = st.session_id
            LEFT JOIN tournament_tasks tt ON s.id = tt.session_id
            GROUP BY s.id, s.byo_config, s.utilities
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
async def get_session_details(session_id: str):
    """Get detailed information for a specific session."""
    try:
        # Get session info
        session_info = await execute_query("""
            SELECT id, byo_config, utilities
            FROM sessions WHERE id = $1
        """, session_id)
        
        if not session_info:
            return jsonify({'error': 'Session not found'}), 404
        
        session = session_info[0]
        
        # Get screening tasks
        screening_tasks = await execute_query("""
            SELECT id, concept, position, response
            FROM screening_tasks 
            WHERE session_id = $1 
            ORDER BY position
        """, session_id)
        
        # Get tournament tasks
        tournament_tasks = await execute_query("""
            SELECT id, task_number, concepts, choice
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
async def get_design_analysis():
    """Analyze designs shown across all sessions."""
    try:
        # Get all screening concepts shown
        screening_concepts = await execute_query("""
            SELECT concept, COUNT(*) as frequency
            FROM screening_tasks 
            GROUP BY concept
            ORDER BY frequency DESC
        """)
        
        # Get all tournament concepts shown
        tournament_concepts = await execute_query("""
            SELECT 
                jsonb_array_elements(concepts) as concept,
                COUNT(*) as frequency
            FROM tournament_tasks 
            GROUP BY jsonb_array_elements(concepts)
            ORDER BY frequency DESC
        """)
        
        # Get attribute level usage
        attribute_usage = await execute_query("""
            WITH concept_data AS (
                SELECT concept FROM screening_tasks
                UNION ALL
                SELECT jsonb_array_elements(concepts) FROM tournament_tasks
            ),
            attribute_levels AS (
                SELECT 
                    jsonb_object_keys(concept) as attribute,
                    jsonb_extract_path_text(concept, jsonb_object_keys(concept)) as level,
                    COUNT(*) as frequency
                FROM concept_data
                GROUP BY attribute, level
            )
            SELECT attribute, level, frequency
            FROM attribute_levels
            ORDER BY attribute, frequency DESC
        """)
        
        return jsonify({
            'screening_concepts': screening_concepts,
            'tournament_concepts': tournament_concepts,
            'attribute_usage': attribute_usage
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/response-analysis')
async def get_response_analysis():
    """Analyze respondent responses and choices."""
    try:
        # Screening response analysis
        screening_responses = await execute_query("""
            SELECT 
                response,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM screening_tasks WHERE response IS NOT NULL), 2) as percentage
            FROM screening_tasks 
            WHERE response IS NOT NULL
            GROUP BY response
        """)
        
        # Tournament choice analysis
        tournament_choices = await execute_query("""
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
        concept_preferences = await execute_query("""
            WITH concept_responses AS (
                SELECT 
                    jsonb_array_elements(concepts) as concept,
                    choice,
                    COUNT(*) as frequency
                FROM tournament_tasks 
                WHERE choice IS NOT NULL
                GROUP BY jsonb_array_elements(concepts), choice
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
async def get_completion_analysis():
    """Analyze completion rates and session flow."""
    try:
        # Session completion flow
        completion_flow = await execute_query("""
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
        session_stats = await execute_query("""
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
        avg_responses = await execute_query("""
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
async def get_attribute_analysis():
    """Analyze attribute preferences and utilities."""
    try:
        # Get all BYO configurations
        byo_configs = await execute_query("""
            SELECT byo_config, COUNT(*) as frequency
            FROM sessions 
            GROUP BY byo_config
            ORDER BY frequency DESC
        """)
        
        # Analyze attribute importance from utilities
        utility_analysis = await execute_query("""
            SELECT 
                utilities,
                COUNT(*) as frequency
            FROM sessions 
            WHERE utilities IS NOT NULL
            GROUP BY utilities
            ORDER BY frequency DESC
        """)
        
        # Attribute level preference analysis
        level_preferences = await execute_query("""
            WITH concept_responses AS (
                SELECT 
                    jsonb_array_elements(concepts) as concept,
                    choice,
                    COUNT(*) as frequency
                FROM tournament_tasks 
                WHERE choice IS NOT NULL
                GROUP BY jsonb_array_elements(concepts), choice
            ),
            attribute_levels AS (
                SELECT 
                    jsonb_object_keys(concept) as attribute,
                    jsonb_extract_path_text(concept, jsonb_object_keys(concept)) as level,
                    SUM(frequency) as total_frequency
                FROM concept_responses
                GROUP BY attribute, level
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
async def export_data():
    """Export all data for analysis."""
    try:
        # Get all sessions with their data
        sessions_data = await execute_query("""
            SELECT 
                s.id,
                s.byo_config,
                s.utilities,
                json_agg(
                    json_build_object(
                        'task_id', st.id,
                        'position', st.position,
                        'concept', st.concept,
                        'response', st.response
                    ) ORDER BY st.position
                ) as screening_tasks,
                json_agg(
                    json_build_object(
                        'task_id', tt.id,
                        'task_number', tt.task_number,
                        'concepts', tt.concepts,
                        'choice', tt.choice
                    ) ORDER BY tt.task_number
                ) as tournament_tasks
            FROM sessions s
            LEFT JOIN screening_tasks st ON s.id = st.session_id
            LEFT JOIN tournament_tasks tt ON s.id = tt.session_id
            GROUP BY s.id, s.byo_config, s.utilities
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