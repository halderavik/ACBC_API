"""
Script to generate sample data for testing the ACBC API Dashboard.
This will create realistic API request data to populate the dashboard.
"""

import sqlite3
import random
import time
import json
from datetime import datetime, timedelta
import uuid

# Database configuration
DB_PATH = "api_monitor.db"

def init_database():
    """Initialize the database with sample data."""
    conn = sqlite3.connect(DB_PATH)
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

def generate_sample_data():
    """Generate realistic sample data for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sample endpoints
    endpoints = [
        "/",
        "/byo",
        "/screening/design",
        "/screening/response",
        "/tournament/design",
        "/tournament/choice-response"
    ]
    
    # Sample methods
    methods = ["GET", "POST"]
    
    # Sample user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "PostmanRuntime/7.32.3",
        "curl/7.88.1"
    ]
    
    # Sample IP addresses
    ip_addresses = [
        "192.168.1.100",
        "10.0.0.50",
        "172.16.0.25",
        "203.0.113.10",
        "198.51.100.5"
    ]
    
    # Sample traffic sources
    sources = ["direct", "google", "facebook", "twitter", "linkedin", "email"]
    
    # Generate sessions
    sessions = []
    for i in range(50):
        session_id = str(uuid.uuid4())
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Random BYO config
        byo_config = {
            "attributes": random.randint(3, 8),
            "levels_per_attribute": random.randint(2, 5),
            "screening_questions": random.randint(5, 15)
        }
        
        screening_completed = random.choice([True, False])
        tournament_completed = random.choice([True, False]) if screening_completed else False
        total_responses = random.randint(0, 20) if screening_completed else 0
        
        sessions.append((
            session_id,
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            json.dumps(byo_config),
            screening_completed,
            tournament_completed,
            total_responses
        ))
    
    # Insert sessions
    cursor.executemany('''
        INSERT INTO sessions (session_id, created_at, byo_config, screening_completed, tournament_completed, total_responses)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sessions)
    
    # Generate API requests
    requests = []
    for i in range(1000):
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        
        # Status codes with realistic distribution
        if random.random() < 0.85:  # 85% success rate
            status_code = 200
        elif random.random() < 0.7:  # 70% of errors are 4xx
            status_code = random.choice([400, 401, 403, 404, 422])
        else:
            status_code = random.choice([500, 502, 503])
        
        response_time = random.uniform(0.1, 2.0)
        user_agent = random.choice(user_agents)
        ip_address = random.choice(ip_addresses)
        session_id = random.choice(sessions)[0] if random.random() < 0.8 else None
        
        error_message = None
        if status_code >= 400:
            error_messages = [
                "Validation error",
                "Resource not found",
                "Unauthorized access",
                "Invalid request format",
                "Database connection error"
            ]
            error_message = random.choice(error_messages)
        
        requests.append((
            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            endpoint,
            method,
            status_code,
            response_time,
            user_agent,
            ip_address,
            session_id,
            error_message
        ))
    
    # Insert requests
    cursor.executemany('''
        INSERT INTO api_requests (timestamp, endpoint, method, status_code, response_time, user_agent, ip_address, session_id, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', requests)
    
    # Generate errors
    errors = []
    for i in range(50):
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        error_types = ["ValidationError", "DatabaseError", "ConnectionError", "TimeoutError", "ValueError"]
        error_type = random.choice(error_types)
        
        error_messages = [
            "Invalid input data provided",
            "Database connection failed",
            "Request timeout exceeded",
            "Required field missing",
            "Invalid session ID"
        ]
        error_message = random.choice(error_messages)
        
        endpoint = random.choice(endpoints)
        stack_trace = f"Traceback (most recent call last):\n  File 'app.py', line {random.randint(1, 100)}, in {error_type.lower()}\n    {error_message}"
        
        errors.append((
            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            error_type,
            error_message,
            endpoint,
            stack_trace
        ))
    
    # Insert errors
    cursor.executemany('''
        INSERT INTO errors (timestamp, error_type, error_message, endpoint, stack_trace)
        VALUES (?, ?, ?, ?, ?)
    ''', errors)
    
    # Generate traffic sources
    traffic = []
    for i in range(200):
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        source = random.choice(sources)
        user_agent = random.choice(user_agents)
        ip_address = random.choice(ip_addresses)
        endpoint = random.choice(endpoints)
        
        traffic.append((
            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            source,
            user_agent,
            ip_address,
            endpoint
        ))
    
    # Insert traffic sources
    cursor.executemany('''
        INSERT INTO traffic_sources (timestamp, source, user_agent, ip_address, endpoint)
        VALUES (?, ?, ?, ?, ?)
    ''', traffic)
    
    conn.commit()
    conn.close()
    
    print("Sample data generated successfully!")
    print(f"- {len(sessions)} sessions created")
    print(f"- {len(requests)} API requests logged")
    print(f"- {len(errors)} errors recorded")
    print(f"- {len(traffic)} traffic sources tracked")

def clear_sample_data():
    """Clear all sample data from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM api_requests')
    cursor.execute('DELETE FROM sessions')
    cursor.execute('DELETE FROM errors')
    cursor.execute('DELETE FROM traffic_sources')
    
    conn.commit()
    conn.close()
    
    print("Sample data cleared successfully!")

if __name__ == "__main__":
    print("ACBC API Dashboard - Sample Data Generator")
    print("=" * 50)
    
    choice = input("Choose an option:\n1. Generate sample data\n2. Clear sample data\n3. Exit\nEnter choice (1-3): ")
    
    if choice == "1":
        init_database()
        generate_sample_data()
    elif choice == "2":
        clear_sample_data()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...") 