from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import subprocess
import models

# Load environment variables from .env file
load_dotenv()

# Get the database URLs from the environment variables
SQLITE_URL = os.getenv("DATABASE_URL")
POSTGRES_URL = os.getenv("POSTGRES_URL")

# Determine which database to use
if POSTGRES_URL:
    SQLALCHEMY_DATABASE_URL = POSTGRES_URL
else:
    SQLALCHEMY_DATABASE_URL = SQLITE_URL

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Function to backup SQLite database
def backup_sqlite():
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        backup_file = "backup_azzamo_banlist.db"
        subprocess.run(["cp", SQLITE_URL.split("///")[-1], backup_file])
        print(f"Backup created: {backup_file}")

# Function to migrate database
def migrate_database():
    # Use Alembic or another migration tool to handle migrations
    # Example: subprocess.run(["alembic", "upgrade", "head"])
    try:
        # Check if tables exist and create them if they don't
        models.Base.metadata.create_all(bind=engine)
        
        # Add missing columns for existing databases
        from sqlalchemy import text
        with engine.connect() as conn:
            try:
                # Check if moderator_name column exists, if not add it
                result = conn.execute(text("PRAGMA table_info(blocked_pubkeys)"))
                columns = [row[1] for row in result.fetchall()]
                if 'moderator_name' not in columns:
                    conn.execute(text("ALTER TABLE blocked_pubkeys ADD COLUMN moderator_name TEXT"))
                    conn.commit()
                    print("Added moderator_name column to blocked_pubkeys table.")
                    
                # Check if audit_logs table has performed_by column
                result = conn.execute(text("PRAGMA table_info(audit_logs)"))
                audit_columns = [row[1] for row in result.fetchall()]
                if 'performed_by' not in audit_columns and 'moderator_name' in audit_columns:
                    # Rename moderator_name to performed_by in audit_logs
                    conn.execute(text("ALTER TABLE audit_logs RENAME COLUMN moderator_name TO performed_by"))
                    conn.commit()
                    print("Renamed moderator_name to performed_by in audit_logs table.")
                elif 'performed_by' not in audit_columns:
                    conn.execute(text("ALTER TABLE audit_logs ADD COLUMN performed_by TEXT"))
                    conn.commit()
                    print("Added performed_by column to audit_logs table.")
            except Exception as e:
                print(f"Note: Column migration may have already been applied: {e}")
        
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}") 
