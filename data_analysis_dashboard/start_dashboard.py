#!/usr/bin/env python3
"""
Startup script for the ACBC Data Analysis Dashboard.
Handles environment setup and launches the dashboard with proper error handling.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask',
        'asyncpg', 
        'pandas',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies!")
            print("   Please run: pip install -r requirements.txt")
            sys.exit(1)
    
    return True

def setup_environment():
    """Setup environment variables if not already set."""
    env_vars = {
        'DATABASE_URL': 'postgresql+asyncpg://postgres:Password123!@localhost:5432/conjoint',
        'API_BASE_URL': 'https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com',
        'PORT': '5001'
    }
    
    print("\n🔧 Environment Setup:")
    for var, default_value in env_vars.items():
        if var not in os.environ:
            os.environ[var] = default_value
            print(f"   {var} = {default_value} (default)")
        else:
            print(f"   {var} = {os.environ[var]} (set)")
    
    print(f"\n💡 To customize, set environment variables:")
    for var in env_vars.keys():
        print(f"   export {var}='your_value'")

def test_database_connection():
    """Test database connection before starting dashboard."""
    print("\n🔍 Testing database connection...")
    
    try:
        # Import and run the test script
        from test_connection import main as test_main
        asyncio.run(test_main())
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure PostgreSQL is running")
        print("   2. Check DATABASE_URL environment variable")
        print("   3. Verify database credentials")
        print("   4. Ensure ACBC tables exist")
        print("\n💡 You can still start the dashboard, but it may not work properly.")
        
        response = input("\nContinue anyway? (y/N): ").lower().strip()
        return response in ['y', 'yes']

def start_dashboard():
    """Start the Flask dashboard."""
    print("\n🚀 Starting ACBC Data Analysis Dashboard...")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        
        port = int(os.environ.get('PORT', 5001))
        host = '0.0.0.0'
        
        print(f"🌐 Dashboard will be available at: http://localhost:{port}")
        print(f"📊 API endpoints available at: http://localhost:{port}/api/")
        print("\n🔄 Starting server... (Press Ctrl+C to stop)")
        print("-" * 50)
        
        app.run(
            host=host,
            port=port,
            debug=False,  # Set to True for development
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start dashboard: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if port 5001 is available")
        print("   2. Verify all dependencies are installed")
        print("   3. Check database connection")
        sys.exit(1)

def main():
    """Main startup function."""
    print("🎯 ACBC Data Analysis Dashboard - Startup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    check_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection failed. Exiting.")
        sys.exit(1)
    
    # Start dashboard
    start_dashboard()

if __name__ == "__main__":
    main() 