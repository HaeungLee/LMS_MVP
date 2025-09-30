#!/usr/bin/env python3
"""
Database setup script for LMS MVP project.
Runs Alembic migrations and seeds initial data.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_migrations():
    """Run Alembic migrations to create database tables."""
    try:
        from alembic.config import Config
        from alembic import command

        # Load Alembic config
        alembic_cfg = Config("alembic.ini")

        # Upgrade to head (latest revision)
        print("Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")

        # Check current revision
        command.current(alembic_cfg)

    except Exception as e:
        print(f"Migration failed: {e}")
        return False
    return True

def run_seeds():
    """Run seed scripts to populate initial data."""
    try:
        print("Running seed scripts...")

        # Import and run seed modules
        import scripts.seed_taxonomy
        print("Taxonomy seeded.")

        import scripts.seed_teacher
        print("Teacher seeded.")

        import scripts.seed_admin
        print("Admin seeded.")

        print("All seeds completed successfully!")
        return True

    except Exception as e:
        print(f"Seeding failed: {e}")
        return False

def main():
    """Main setup function."""
    print("Starting LMS MVP database setup...")

    # Change to backend directory
    os.chdir(backend_dir)

    # Run migrations
    if not run_migrations():
        sys.exit(1)

    # Run seeds
    if not run_seeds():
        sys.exit(1)

    print("Database setup completed!")

if __name__ == "__main__":
    main()