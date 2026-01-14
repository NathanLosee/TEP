#!/usr/bin/env python3
"""Database Restore Script for TEP.

Restores a database from a backup file.

Usage:
    python restore_database.py /path/to/backup.sqlite
    python restore_database.py /path/to/backup.sqlite.gz --decompress
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_DB_PATH = Path("tep.sqlite")


def restore_database(
    backup_path: Path,
    db_path: Path,
    decompress: bool = False,
    no_backup: bool = False
) -> bool:
    """Restore database from backup.

    Args:
        backup_path: Path to the backup file
        db_path: Path to the database file to restore to
        decompress: Whether to decompress the backup
        no_backup: Skip creating safety backup of current database

    Returns:
        bool: True if restore succeeded

    Raises:
        FileNotFoundError: If backup file doesn't exist
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    # Create safety backup of current database
    if db_path.exists() and not no_backup:
        print(f"Creating safety backup of current database...")
        safety_backup = db_path.parent / f"{db_path.stem}_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
        shutil.copy2(db_path, safety_backup)
        print(f"  Safety backup created: {safety_backup}")

    print(f"Restoring database from: {backup_path}")

    try:
        if decompress:
            import gzip
            print("  Decompressing backup...")
            with gzip.open(backup_path, 'rb') as f_in:
                with open(db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(backup_path, db_path)

        print(f"✓ Database restored successfully to: {db_path}")

        # Get file size
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"  Database size: {size_mb:.2f} MB")

        return True

    except Exception as e:
        print(f"✗ Error restoring database: {e}")
        return False


def verify_database(db_path: Path) -> bool:
    """Verify database integrity using SQLite pragma.

    Args:
        db_path: Path to the database file

    Returns:
        bool: True if database is valid
    """
    try:
        import sqlite3
        print(f"Verifying database integrity...")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check integrity
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]

        conn.close()

        if result == "ok":
            print("✓ Database integrity check passed")
            return True
        else:
            print(f"✗ Database integrity check failed: {result}")
            return False

    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        return False


def main():
    """Main entry point for the restore script."""
    parser = argparse.ArgumentParser(
        description="TEP Database Restore Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Restore from backup
  python restore_database.py backups/tep_20260113_120000.sqlite

  # Restore from compressed backup
  python restore_database.py backups/tep_20260113_120000.sqlite.gz --decompress

  # Restore to custom location
  python restore_database.py backups/tep_backup.sqlite --db-path /path/to/tep.sqlite

  # Skip safety backup (not recommended)
  python restore_database.py backups/tep_backup.sqlite --no-backup

WARNING: This will replace your current database. Always ensure you have
         a recent backup before performing a restore.
        """
    )

    parser.add_argument(
        "backup_file",
        type=Path,
        help="Path to backup file to restore from"
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to database file (default: {DEFAULT_DB_PATH})"
    )

    parser.add_argument(
        "--decompress",
        action="store_true",
        help="Decompress backup (use for .gz files)"
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating safety backup of current database (not recommended)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify database integrity after restore"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    try:
        # Confirmation prompt
        if not args.force:
            print("=" * 70)
            print("WARNING: This will replace your current database!")
            print("=" * 70)
            print(f"Backup file: {args.backup_file}")
            print(f"Target database: {args.db_path}")

            if not args.no_backup and args.db_path.exists():
                print("A safety backup will be created before restore.")
            print("=" * 70)

            response = input("Continue with restore? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Restore cancelled.")
                return 0

        # Auto-detect compression from filename
        if args.backup_file.suffix == '.gz' and not args.decompress:
            print("Detected .gz file, enabling decompression automatically")
            args.decompress = True

        # Perform restore
        if restore_database(
            args.backup_file,
            args.db_path,
            args.decompress,
            args.no_backup
        ):
            # Verify if requested
            if args.verify:
                print()
                if not verify_database(args.db_path):
                    print("✗ Database verification failed")
                    return 1

            print()
            print("✓ Restore operation completed successfully")
            print()
            print("IMPORTANT: Restart the TEP service for changes to take effect.")
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        print("\nRestore cancelled by user")
        return 130
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
