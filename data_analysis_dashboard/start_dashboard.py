#!/usr/bin/env python3
"""
Data Analysis Dashboard Startup Script

This script starts the ACBC Data Analysis Dashboard with proper configuration.
It handles virtual environment activation and runs the dashboard with Hypercorn ASGI server.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """Main startup function."""
    print("🚀 Starting ACBC Data Analysis Dashboard...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Check if virtual environment exists
    venv_path = script_dir / "venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv venv")
        print("Then activate it and install requirements:")
        print("  venv\\Scripts\\activate  # Windows")
        print("  source venv/bin/activate  # macOS/Linux")
        print("  pip install -r requirements.txt")
        return 1
    
    # Determine the Python executable path
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        hypercorn_exe = venv_path / "Scripts" / "hypercorn.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        hypercorn_exe = venv_path / "bin" / "hypercorn"
    
    # Check if Hypercorn is installed
    if not hypercorn_exe.exists():
        print("❌ Hypercorn not found in virtual environment!")
        print("Please install requirements:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Check if app.py exists
    app_file = script_dir / "app.py"
    if not app_file.exists():
        print("❌ app.py not found!")
        return 1
    
    print("✅ Virtual environment found")
    print("✅ Hypercorn found")
    print("✅ app.py found")
    print("🌐 Starting dashboard on http://localhost:5001")
    print("📊 Data Analysis Dashboard will be available at: http://localhost:5001")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the dashboard with Hypercorn
        cmd = [str(hypercorn_exe), "app:app", "--bind", "0.0.0.0:5001", "--reload"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 