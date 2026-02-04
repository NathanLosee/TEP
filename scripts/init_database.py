#!/usr/bin/env python3
"""Database Initialization Script for TAP.

Creates and initializes the TAP database with proper schema.

Usage:
    python init_database.py
    python init_database.py --db-path /path/to/tap.sqlite
    python init_database.py --force
"""

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_DB_PATH = Path("tap.sqlite")


def check_alembic_available() -> bool:
    """Check if Alembic is available.

    Returns:
        bool: True if Alembic is available
    """
    try:
        result = subprocess.run(
            ["alembic", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def init_database(db_path: Path, force: bool = False) -> bool:
    """Initialize database with schema.

    Args:
        db_path: Path to the database file
        force: Force initialization even if database exists

    Returns:
        bool: True if initialization succeeded
    """
    # Check if database already exists
    if db_path.exists() and not force:
        print(f"✗ Database already exists: {db_path}")
        print("  Use --force to reinitialize (this will delete existing data)")
        return False

    if db_path.exists() and force:
        print(f"Removing existing database: {db_path}")
        try:
            db_path.unlink()
            print("✓ Existing database removed")
        except Exception as e:
            print(f"✗ Error removing existing database: {e}")
            return False

    print(f"Initializing new database: {db_path}")

    # Create database directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if alembic is available
    if not check_alembic_available():
        print("✗ Alembic not found. Please install with: pip install alembic")
        return False

    # Run Alembic migrations to create schema
    print("Running database migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout:
            print(result.stdout)

        print("✓ Database schema created successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Error running migrations: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def verify_database(db_path: Path) -> bool:
    """Verify database structure.

    Args:
        db_path: Path to the database file

    Returns:
        bool: True if database structure is valid
    """
    try:
        import sqlite3

        print("Verifying database structure...")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
        tables = [row[0] for row in cursor.fetchall()]

        conn.close()

        expected_tables = [
            "alembic_version",
            "auth_roles",
            "auth_role_permissions",
            "auth_role_memberships",
            "departments",
            "department_memberships",
            "employees",
            "event_logs",
            "holiday_groups",
            "holidays",
            "licenses",
            "org_units",
            "registered_browsers",
            "timeclock_entries",
            "users",
        ]

        print(f"  Found {len(tables)} tables:")
        for table in tables:
            print(f"    - {table}")

        # Check if all expected tables exist
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"✗ Missing tables: {', '.join(missing_tables)}")
            return False

        print("✓ Database structure verified")
        return True

    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        return False


def main():
    """Main entry point for the initialization script."""
    parser = argparse.ArgumentParser(
        description="TAP Database Initialization Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script initializes a new TAP database by running Alembic migrations
to create the database schema.

Examples:
  # Initialize default database
  python init_database.py

  # Initialize custom database location
  python init_database.py --db-path /path/to/tap.sqlite

  # Force reinitialize (deletes existing data)
  python init_database.py --force

  # Initialize and verify
  python init_database.py --verify

Notes:
  - Requires Alembic to be installed
  - Creates root user automatically on first application start
  - Use --force carefully as it will delete existing data
        """,
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to database file (default: {DEFAULT_DB_PATH})",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force initialization even if database exists (deletes existing data)",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify database structure after initialization",
    )

    args = parser.parse_args()

    try:
        # Confirmation for force mode
        if args.db_path.exists() and args.force:
            print("=" * 70)
            print("WARNING: Force mode will delete the existing database!")
            print("=" * 70)
            print(f"Database: {args.db_path}")
            print("=" * 70)

            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("Initialization cancelled.")
                return 0

        # Initialize database
        if init_database(args.db_path, args.force):
            # Verify if requested
            if args.verify:
                print()
                if not verify_database(args.db_path):
                    print("✗ Database verification failed")
                    return 1

            print()
            print("✓ Database initialization completed successfully")
            print()
            print("Next staps:")
            print("  1. Start the TAP application")
            print("  2. Root user will be created automatically")
            print("  3. Login with username '0' and the displayed password")
            print("  4. Activate your license in the admin panel")
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        print("\nInitialization cancelled by user")
        return 130
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
