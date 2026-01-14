#!/usr/bin/env python3
"""Database Backup Script for TEP.

Creates timestamped backups of the SQLite database with optional compression.

Usage:
    python backup_database.py
    python backup_database.py --output-dir /path/to/backups
    python backup_database.py --compress
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_DB_PATH = Path("tep.sqlite")
DEFAULT_BACKUP_DIR = Path("backups")


def backup_database(
    db_path: Path,
    backup_dir: Path,
    compress: bool = False
) -> Path:
    """Create a backup of the database.

    Args:
        db_path: Path to the database file
        backup_dir: Directory to store backups
        compress: Whether to compress the backup

    Returns:
        Path: Path to the backup file

    Raises:
        FileNotFoundError: If database file doesn't exist
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"tep_{timestamp}.sqlite"

    if compress:
        backup_path = backup_dir / f"{backup_name}.gz"
    else:
        backup_path = backup_dir / backup_name

    print(f"Creating backup of {db_path}...")
    print(f"Backup destination: {backup_path}")

    # Copy database file
    if compress:
        import gzip
        with open(db_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        shutil.copy2(db_path, backup_path)

    # Get file size
    size_mb = backup_path.stat().st_size / (1024 * 1024)

    print(f"✓ Backup created successfully")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"  Location: {backup_path}")

    return backup_path


def cleanup_old_backups(backup_dir: Path, keep_count: int = 30):
    """Remove old backups, keeping only the most recent ones.

    Args:
        backup_dir: Directory containing backups
        keep_count: Number of recent backups to keep
    """
    if not backup_dir.exists():
        return

    # Find all backup files
    backups = sorted(
        backup_dir.glob("tep_*.sqlite*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    # Remove old backups
    removed_count = 0
    for backup in backups[keep_count:]:
        print(f"Removing old backup: {backup.name}")
        backup.unlink()
        removed_count += 1

    if removed_count > 0:
        print(f"✓ Removed {removed_count} old backup(s)")


def main():
    """Main entry point for the backup script."""
    parser = argparse.ArgumentParser(
        description="TEP Database Backup Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic backup
  python backup_database.py

  # Backup with compression
  python backup_database.py --compress

  # Specify custom paths
  python backup_database.py --db-path /path/to/tep.sqlite --output-dir /path/to/backups

  # Cleanup old backups (keep 30 most recent)
  python backup_database.py --cleanup --keep 30
        """
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to database file (default: {DEFAULT_DB_PATH})"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_BACKUP_DIR,
        help=f"Backup output directory (default: {DEFAULT_BACKUP_DIR})"
    )

    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress backup with gzip"
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove old backups"
    )

    parser.add_argument(
        "--keep",
        type=int,
        default=30,
        help="Number of recent backups to keep when cleaning up (default: 30)"
    )

    args = parser.parse_args()

    try:
        # Create backup
        if not args.cleanup:
            backup_path = backup_database(
                args.db_path,
                args.output_dir,
                args.compress
            )
            print()

        # Cleanup old backups if requested
        if args.cleanup:
            print(f"Cleaning up old backups (keeping {args.keep} most recent)...")
            cleanup_old_backups(args.output_dir, args.keep)
            print()

        print("✓ Backup operation completed successfully")
        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
