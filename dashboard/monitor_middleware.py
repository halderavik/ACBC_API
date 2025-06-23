"""
Monitoring middleware for FastAPI to automatically log API requests and errors.
This can be integrated with your existing ACBC API to provide real-time monitoring.
"""

import time
import json
import sqlite3
import traceback
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

# Database configuration
DB_PATH = "api_monitor.db"

class APIMonitor:
    """API monitoring class for tracking requests, errors, and performance."""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize the API monitor with database path."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the monitoring database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
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
                error_message TEXT,
                request_body TEXT,
                response_body TEXT
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
                stack_trace TEXT,
                request_body TEXT
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
    
    def log_request(self, request: Request, response: Response, response_time: float, 
                   error_message: str = None, request_body: str = None, response_body: str = None):
        """Log API request details to the database."""
        try:
            # Extract session ID from headers or query params
            session_id = request.headers.get('X-Session-ID') or request.query_params.get('session_id')
            
            # Extract IP address
            ip_address = request.client.host if request.client else "unknown"
            
            # Extract user agent
            user_agent = request.headers.get('user-agent', 'unknown')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_requests 
                (endpoint, method, status_code, response_time, user_agent, ip_address, 
                 session_id, error_message, request_body, response_body)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(request.url.path),
                request.method,
                response.status_code,
                response_time,
                user_agent,
                ip_address,
                session_id,
                error_message,
                request_body,
                response_body
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging request: {e}")
    
    def log_error(self, request: Request, error: Exception, request_body: str = None):
        """Log error details to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO errors (error_type, error_message, endpoint, stack_trace, request_body)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                type(error).__name__,
                str(error),
                str(request.url.path),
                traceback.format_exc(),
                request_body
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging error: {e}")
    
    def log_traffic_source(self, request: Request, source: str = "direct"):
        """Log traffic source information."""
        try:
            ip_address = request.client.host if request.client else "unknown"
            user_agent = request.headers.get('user-agent', 'unknown')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO traffic_sources (source, user_agent, ip_address, endpoint)
                VALUES (?, ?, ?, ?)
            ''', (source, user_agent, ip_address, str(request.url.path)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging traffic source: {e}")
    
    def update_session(self, session_id: str, **kwargs):
        """Update session information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if session exists
            cursor.execute('SELECT id FROM sessions WHERE session_id = ?', (session_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing session
                set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [session_id]
                cursor.execute(f'UPDATE sessions SET {set_clause} WHERE session_id = ?', values)
            else:
                # Create new session
                columns = ['session_id'] + list(kwargs.keys())
                placeholders = ', '.join(['?' for _ in range(len(columns))])
                values = [session_id] + list(kwargs.values())
                cursor.execute(f'INSERT INTO sessions ({", ".join(columns)}) VALUES ({placeholders})', values)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating session: {e}")

# Global monitor instance
monitor = APIMonitor()

async def monitoring_middleware(request: Request, call_next: Callable) -> Response:
    """FastAPI middleware for monitoring requests."""
    start_time = time.time()
    
    # Extract request body if needed
    request_body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                request_body = body.decode('utf-8')
        except:
            pass
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Extract response body if needed
        response_body = None
        if hasattr(response, 'body'):
            try:
                response_body = response.body.decode('utf-8')
            except:
                pass
        
        # Log the request
        monitor.log_request(request, response, response_time, 
                          request_body=request_body, response_body=response_body)
        
        # Log traffic source
        monitor.log_traffic_source(request)
        
        return response
        
    except Exception as e:
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log the error
        monitor.log_error(request, e, request_body)
        
        # Create error response
        error_response = JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )
        
        # Log the error request
        monitor.log_request(request, error_response, response_time, 
                          error_message=str(e), request_body=request_body)
        
        return error_response

# Utility functions for manual logging
def log_session_creation(session_id: str, byo_config: Dict[str, Any] = None):
    """Log when a new session is created."""
    monitor.update_session(session_id, byo_config=json.dumps(byo_config) if byo_config else None)

def log_screening_completion(session_id: str):
    """Log when screening is completed."""
    monitor.update_session(session_id, screening_completed=True)

def log_tournament_completion(session_id: str):
    """Log when tournament is completed."""
    monitor.update_session(session_id, tournament_completed=True)

def log_response_count(session_id: str, count: int):
    """Log response count for a session."""
    monitor.update_session(session_id, total_responses=count)

# Example usage in FastAPI app:
"""
from fastapi import FastAPI
from monitor_middleware import monitoring_middleware

app = FastAPI()

# Add the monitoring middleware
app.middleware("http")(monitoring_middleware)

# In your route handlers, you can manually log specific events:
@app.post("/byo")
async def create_byo_config(request: Request):
    # Your existing logic here
    
    # Log session creation
    log_session_creation(session_id, byo_config)
    
    return response

@app.post("/screening/response")
async def submit_screening_response(request: Request):
    # Your existing logic here
    
    # Log screening completion
    log_screening_completion(session_id)
    
    return response
""" 