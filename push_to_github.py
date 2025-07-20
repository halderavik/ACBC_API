#!/usr/bin/env python3
"""
Python script to push changes to GitHub and Heroku
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to push changes."""
    print("🚀 Pushing changes to GitHub and Heroku...")
    
    # Check if we're in the right directory
    if not os.path.exists("backend"):
        print("❌ Error: backend directory not found. Please run this script from the ACBC project root.")
        return False
    
    # Git commands to run
    commands = [
        ("git status", "Checking git status"),
        ("git add .", "Adding all changes"),
        ("git commit -m \"Fix 500 error on BYO config endpoint - v1.4.3\"", "Committing changes"),
        ("git remote add origin https://github.com/halderavik/ACBC_API.git", "Adding GitHub remote"),
        ("git push -u origin main", "Pushing to GitHub"),
        ("git push heroku main", "Pushing to Heroku")
    ]
    
    # Run each command
    for command, description in commands:
        if not run_command(command, description):
            print(f"❌ Failed at: {description}")
            return False
    
    print("✅ All changes pushed successfully!")
    print("🌐 GitHub: https://github.com/halderavik/ACBC_API.git")
    print("🚀 Heroku: https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 