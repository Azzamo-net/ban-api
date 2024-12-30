from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import subprocess

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
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}") 
