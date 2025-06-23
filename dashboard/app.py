from flask import Flask, render_template, jsonify, request
import requests
import sqlite3
import json
import datetime
import os
from collections import defaultdict
import threading
import time

app = Flask(__name__)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com")
DB_PATH = os.getenv("DB_PATH", "api_monitor.db")
PORT = int(os.getenv("PORT", 5000))

# Initialize database
def init_db():
    """Initialize the SQLite database for storing monitoring data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables for monitoring
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            endpoint TEXT,
            method TEXT,
            status_code INTEGER,
            response_time REAL,
            user_agent TEXT,
            ip_address TEXT,
            session_id TEXT,
            error_message TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            byo_config TEXT,
            screening_completed BOOLEAN DEFAULT FALSE,
            tournament_completed BOOLEAN DEFAULT FALSE,
            total_responses INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            error_type TEXT,
            error_message TEXT,
            endpoint TEXT,
            stack_trace TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            user_agent TEXT,
            ip_address TEXT,
            endpoint TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# API monitoring functions
def log_api_request(endpoint, method, status_code, response_time, user_agent, ip_address, session_id=None, error_message=None):
    """Log API request details to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO api_requests (endpoint, method, status_code, response_time, user_agent, ip_address, session_id, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (endpoint, method, status_code, response_time, user_agent, ip_address, session_id, error_message))
    
    conn.commit()
    conn.close()

def log_error(error_type, error_message, endpoint, stack_trace=None):
    """Log errors to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO errors (error_type, error_message, endpoint, stack_trace)
        VALUES (?, ?, ?, ?)
    ''', (error_type, error_message, endpoint, stack_trace))
    
    conn.commit()
    conn.close()

def log_traffic_source(source, user_agent, ip_address, endpoint):
    """Log traffic source information."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO traffic_sources (source, user_agent, ip_address, endpoint)
        VALUES (?, ?, ?, ?)
    ''', (source, user_agent, ip_address, endpoint))
    
    conn.commit()
    conn.close()

# Dashboard routes
@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get API statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get total requests
    cursor.execute('SELECT COUNT(*) FROM api_requests')
    total_requests = cursor.fetchone()[0]
    
    # Get requests in last 24 hours
    cursor.execute('''
        SELECT COUNT(*) FROM api_requests 
        WHERE timestamp >= datetime('now', '-1 day')
    ''')
    requests_24h = cursor.fetchone()[0]
    
    # Get error count
    cursor.execute('SELECT COUNT(*) FROM errors WHERE timestamp >= datetime("now", "-1 day")')
    errors_24h = cursor.fetchone()[0]
    
    # Get average response time
    cursor.execute('SELECT AVG(response_time) FROM api_requests WHERE response_time IS NOT NULL')
    avg_response_time = cursor.fetchone()[0] or 0
    
    # Get active sessions
    cursor.execute('SELECT COUNT(*) FROM sessions WHERE created_at >= datetime("now", "-7 days")')
    active_sessions = cursor.fetchone()[0]
    
    # Get endpoint usage
    cursor.execute('''
        SELECT endpoint, COUNT(*) as count 
        FROM api_requests 
        WHERE timestamp >= datetime('now', '-1 day')
        GROUP BY endpoint 
        ORDER BY count DESC
    ''')
    endpoint_usage = dict(cursor.fetchall())
    
    # Get status code distribution
    cursor.execute('''
        SELECT status_code, COUNT(*) as count 
        FROM api_requests 
        WHERE timestamp >= datetime('now', '-1 day')
        GROUP BY status_code
    ''')
    status_codes = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        'total_requests': total_requests,
        'requests_24h': requests_24h,
        'errors_24h': errors_24h,
        'avg_response_time': round(avg_response_time, 2),
        'active_sessions': active_sessions,
        'endpoint_usage': endpoint_usage,
        'status_codes': status_codes
    })

@app.route('/api/recent-requests')
def get_recent_requests():
    """Get recent API requests."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, endpoint, method, status_code, response_time, session_id, error_message
        FROM api_requests 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    
    requests = []
    for row in cursor.fetchall():
        requests.append({
            'timestamp': row[0],
            'endpoint': row[1],
            'method': row[2],
            'status_code': row[3],
            'response_time': row[4],
            'session_id': row[5],
            'error_message': row[6]
        })
    
    conn.close()
    return jsonify(requests)

@app.route('/api/recent-errors')
def get_recent_errors():
    """Get recent errors."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, error_type, error_message, endpoint
        FROM errors 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''')
    
    errors = []
    for row in cursor.fetchall():
        errors.append({
            'timestamp': row[0],
            'error_type': row[1],
            'error_message': row[2],
            'endpoint': row[3]
        })
    
    conn.close()
    return jsonify(errors)

@app.route('/api/traffic-sources')
def get_traffic_sources():
    """Get traffic source statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get traffic by source
    cursor.execute('''
        SELECT source, COUNT(*) as count 
        FROM traffic_sources 
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY source 
        ORDER BY count DESC
    ''')
    sources = dict(cursor.fetchall())
    
    # Get user agents
    cursor.execute('''
        SELECT user_agent, COUNT(*) as count 
        FROM traffic_sources 
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY user_agent 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    user_agents = dict(cursor.fetchall())
    
    conn.close()
    return jsonify({
        'sources': sources,
        'user_agents': user_agents
    })

@app.route('/api/sessions')
def get_sessions():
    """Get session statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get session completion rates
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN screening_completed = 1 THEN 1 ELSE 0 END) as screening_completed,
            SUM(CASE WHEN tournament_completed = 1 THEN 1 ELSE 0 END) as tournament_completed
        FROM sessions 
        WHERE created_at >= datetime('now', '-7 days')
    ''')
    
    row = cursor.fetchone()
    completion_stats = {
        'total': row[0],
        'screening_completed': row[1],
        'tournament_completed': row[2]
    }
    
    # Get recent sessions
    cursor.execute('''
        SELECT session_id, created_at, screening_completed, tournament_completed, total_responses
        FROM sessions 
        ORDER BY created_at DESC 
        LIMIT 20
    ''')
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'session_id': row[0],
            'created_at': row[1],
            'screening_completed': bool(row[2]),
            'tournament_completed': bool(row[3]),
            'total_responses': row[4]
        })
    
    conn.close()
    return jsonify({
        'completion_stats': completion_stats,
        'recent_sessions': sessions
    })

# API health check
@app.route('/api/health-check')
def health_check():
    """Check the health of the monitored API."""
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        response_time = time.time() - start_time
        
        log_api_request(
            endpoint="/",
            method="GET",
            status_code=response.status_code,
            response_time=response_time,
            user_agent="Dashboard-Health-Check",
            ip_address="127.0.0.1"
        )
        
        return jsonify({
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response_time,
            'status_code': response.status_code
        })
    except Exception as e:
        log_error('health_check_failed', str(e), '/')
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start the dashboard
    app.run(debug=False, host='0.0.0.0', port=PORT) 