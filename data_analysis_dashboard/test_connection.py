#!/usr/bin/env python3
"""
Test script to verify database connection and data availability for the ACBC Data Analysis Dashboard.
"""

import asyncio
import asyncpg
import os
import json
from datetime import datetime

# Configuration - Updated to use actual database settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:Password123!@localhost:5432/conjoint")

# Convert SQLAlchemy URL format to asyncpg format
def convert_database_url(url):
    """Convert SQLAlchemy URL format to asyncpg format."""
    if url.startswith("postgresql+asyncpg://"):
        # Remove the +asyncpg part and convert to asyncpg format
        return url.replace("postgresql+asyncpg://", "postgresql://")
    return url

# Use the converted database URL
ASYNC_DATABASE_URL = convert_database_url(DATABASE_URL)

async def test_database_connection():
    """Test database connection and basic queries."""
    print("🔍 Testing ACBC Data Analysis Dashboard Database Connection")
    print("=" * 60)
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        print(f"🔗 Database URL: {ASYNC_DATABASE_URL}")
        conn = await asyncpg.connect(ASYNC_DATABASE_URL)
        print("✅ Database connection successful!")
        
        # Test basic queries
        print("\n📊 Testing basic queries...")
        
        # Check if tables exist
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('sessions', 'screening_tasks', 'tournament_tasks')
            ORDER BY table_name
        """
        tables = await conn.fetch(tables_query)
        print(f"📋 Found tables: {[t['table_name'] for t in tables]}")
        
        if not tables:
            print("❌ Required tables not found!")
            return False
        
        # Count sessions
        sessions_count = await conn.fetchval("SELECT COUNT(*) FROM sessions")
        print(f"👥 Total sessions: {sessions_count}")
        
        # Count screening tasks
        screening_count = await conn.fetchval("SELECT COUNT(*) FROM screening_tasks")
        print(f"📝 Total screening tasks: {screening_count}")
        
        # Count tournament tasks
        tournament_count = await conn.fetchval("SELECT COUNT(*) FROM tournament_tasks")
        print(f"🏆 Total tournament tasks: {tournament_count}")
        
        # Check for recent sessions (without created_at column)
        recent_sessions = await conn.fetch("""
            SELECT id, byo_config
            FROM sessions 
            LIMIT 5
        """)
        
        print(f"\n🕒 Recent sessions:")
        for session in recent_sessions:
            print(f"   - {session['id']}: {len(str(session['byo_config']))} chars config")
        
        # Test completion statistics
        completion_stats = await conn.fetchrow("""
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
        
        print(f"\n📈 Completion Statistics:")
        print(f"   - Total sessions: {completion_stats['total_sessions']}")
        print(f"   - Screening started: {completion_stats['screening_started']}")
        print(f"   - Tournament started: {completion_stats['tournament_started']}")
        print(f"   - Tournament completed: {completion_stats['tournament_completed']}")
        
        # Test design analysis query
        print(f"\n🎨 Testing design analysis...")
        screening_concepts = await conn.fetch("""
            SELECT concept, COUNT(*) as frequency
            FROM screening_tasks 
            GROUP BY concept
            ORDER BY frequency DESC
            LIMIT 3
        """)
        
        print(f"📊 Top screening concepts: {len(screening_concepts)} found")
        for concept in screening_concepts:
            print(f"   - Concept shown {concept['frequency']} times")
        
        # Test response analysis query
        print(f"\n📊 Testing response analysis...")
        screening_responses = await conn.fetch("""
            SELECT 
                response,
                COUNT(*) as count
            FROM screening_tasks 
            WHERE response IS NOT NULL
            GROUP BY response
        """)
        
        print(f"📝 Screening responses:")
        for response in screening_responses:
            print(f"   - {response['response']}: {response['count']} responses")
        
        # Test tournament choices
        tournament_choices = await conn.fetch("""
            SELECT 
                choice,
                COUNT(*) as count
            FROM tournament_tasks 
            WHERE choice IS NOT NULL
            GROUP BY choice
            ORDER BY choice
        """)
        
        print(f"🏆 Tournament choices:")
        for choice in tournament_choices:
            print(f"   - Choice {choice['choice']}: {choice['count']} selections")
        
        await conn.close()
        print(f"\n✅ All tests completed successfully!")
        print(f"🎉 Dashboard should work with this database!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"\n🔧 Troubleshooting tips:")
        print(f"   1. Check DATABASE_URL environment variable")
        print(f"   2. Ensure PostgreSQL is running")
        print(f"   3. Verify database credentials")
        print(f"   4. Check if ACBC tables exist")
        print(f"   5. Current DATABASE_URL: {ASYNC_DATABASE_URL}")
        return False

async def test_dashboard_queries():
    """Test the actual dashboard queries."""
    print(f"\n🧪 Testing Dashboard Queries")
    print("=" * 40)
    
    try:
        conn = await asyncpg.connect(ASYNC_DATABASE_URL)
        
        # Test sessions overview query (without created_at)
        print("📊 Testing sessions overview...")
        sessions_overview = await conn.fetch("""
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
            LIMIT 5
        """)
        
        print(f"✅ Sessions overview query: {len(sessions_overview)} sessions found")
        
        # Test design analysis query
        print("🎨 Testing design analysis...")
        design_analysis = await conn.fetch("""
            SELECT concept, COUNT(*) as frequency
            FROM screening_tasks 
            GROUP BY concept
            ORDER BY frequency DESC
            LIMIT 5
        """)
        
        print(f"✅ Design analysis query: {len(design_analysis)} concepts found")
        
        # Test response analysis query
        print("📝 Testing response analysis...")
        response_analysis = await conn.fetch("""
            SELECT 
                response,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM screening_tasks WHERE response IS NOT NULL), 2) as percentage
            FROM screening_tasks 
            WHERE response IS NOT NULL
            GROUP BY response
        """)
        
        print(f"✅ Response analysis query: {len(response_analysis)} response types found")
        
        # Test completion analysis query
        print("✅ Testing completion analysis...")
        completion_analysis = await conn.fetch("""
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
        
        print(f"✅ Completion analysis query: {len(completion_analysis)} metrics calculated")
        
        await conn.close()
        print(f"\n🎉 All dashboard queries working correctly!")
        
    except Exception as e:
        print(f"❌ Dashboard query error: {str(e)}")

def main():
    """Main test function."""
    print("🚀 ACBC Data Analysis Dashboard - Connection Test")
    print("=" * 60)
    print(f"📅 Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Database URL: {ASYNC_DATABASE_URL}")
    print()
    
    # Run tests
    success = asyncio.run(test_database_connection())
    
    if success:
        asyncio.run(test_dashboard_queries())
        print(f"\n🎯 Dashboard is ready to run!")
        print(f"💡 Run: python app.py")
    else:
        print(f"\n❌ Please fix database connection issues before running the dashboard")

if __name__ == "__main__":
    main() 