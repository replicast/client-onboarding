"""
Create database schema in Azure SQL Database

This script creates all tables defined in the SQLAlchemy models.
Run this once to set up your database schema.
"""
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base
from app.models.client import Client
from app.models.site import Site


def create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")
    print(f"Database: {engine.url}")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("\n✓ Successfully created all tables:")
        print("  - clients")
        print("  - sites")
        print("\nDatabase schema is ready!")

    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_tables()
