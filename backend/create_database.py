"""
Script to create the conjoint database.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the conjoint database."""
    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return
    
    # Convert async URL to sync URL for database creation
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Extract database name from URL
    # Format: postgresql://user:password@host:port/database
    parts = sync_url.split("/")
    if len(parts) >= 4:
        db_name = parts[-1]
        # Create URL without database name
        base_url = "/".join(parts[:-1])
        
        try:
            # Connect to PostgreSQL server (without specifying database)
            engine = create_engine(base_url)
            
            with engine.connect() as conn:
                # Check if database already exists
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if result.fetchone():
                    print(f"Database '{db_name}' already exists")
                else:
                    # Create the database
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    conn.commit()
                    print(f"Database '{db_name}' created successfully")
                    
        except Exception as e:
            print(f"Error creating database: {e}")
            print("Please check your PostgreSQL credentials and make sure PostgreSQL is running")
    else:
        print("Invalid DATABASE_URL format")

if __name__ == "__main__":
    create_database() 