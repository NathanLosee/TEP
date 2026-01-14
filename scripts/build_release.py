#!/usr/bin/env python3
"""Build script for creating TEP production release package.

This script automates the process of building a production-ready TEP package
including backend, frontend, database, and all necessary assets.

Usage:
    python build_release.py --version 1.0.0
    python build_release.py --version 1.0.0 --output-dir dist
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(message: str):
    """Print a build step message."""
    print(f"\n{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*60}{Colors.ENDC}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}", file=sys.stderr)


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(cmd: list, cwd: Path = None) -> bool:
    """Run a command and return success status.

    Args:
        cmd: Command to run as list
        cwd: Working directory for command

    Returns:
        bool: True if command succeeded
    """
    try:
        print(f"Running: {' '.join(str(c) for c in cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def check_prerequisites() -> bool:
    """Check that required tools are available.

    Returns:
        bool: True if all prerequisites are met
    """
    print_step("Checking Prerequisites")

    prerequisites = [
        ("poetry", ["poetry", "--version"]),
        ("node", ["node", "--version"]),
        ("npm", ["npm", "--version"]),
    ]

    all_ok = True
    for name, cmd in prerequisites:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print_success(f"{name}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error(f"{name} not found")
            all_ok = False

    return all_ok


def run_tests() -> bool:
    """Run all tests to ensure code quality.

    Returns:
        bool: True if all tests pass
    """
    print_step("Running Tests")

    # Backend tests
    print("Running backend tests...")
    if not run_command(["poetry", "run", "pytest", "tests/", "-v"]):
        print_error("Backend tests failed")
        return False
    print_success("Backend tests passed")

    # Frontend tests
    print("\nRunning frontend tests...")
    if not run_command(
        ["npm", "test", "--", "--watch=false", "--browsers=ChromeHeadless"],
        cwd=Path("frontend")
    ):
        print_error("Frontend tests failed")
        return False
    print_success("Frontend tests passed")

    return True


def build_frontend(output_dir: Path) -> bool:
    """Build frontend production bundle.

    Args:
        output_dir: Directory for build output

    Returns:
        bool: True if build succeeded
    """
    print_step("Building Frontend")

    frontend_dir = Path("frontend")
    dist_dir = frontend_dir / "dist" / "tep-frontend" / "browser"

    # Build production bundle
    print("Building Angular production bundle...")
    if not run_command(["npm", "run", "build", "--", "--configuration=production"], cwd=frontend_dir):
        print_error("Frontend build failed")
        return False

    # Copy built files to output
    if dist_dir.exists():
        frontend_output = output_dir / "frontend"
        shutil.copytree(dist_dir, frontend_output, dirs_exist_ok=True)
        print_success(f"Frontend built to: {frontend_output}")
        return True
    else:
        print_error(f"Build output not found at: {dist_dir}")
        return False


def build_backend(output_dir: Path) -> bool:
    """Build backend package.

    Args:
        output_dir: Directory for build output

    Returns:
        bool: True if build succeeded
    """
    print_step("Building Backend")

    backend_output = output_dir / "backend"
    backend_output.mkdir(parents=True, exist_ok=True)

    # Copy source files
    print("Copying backend source files...")
    src_files = [
        "src",
        "alembic",
        "alembic.ini",
        "pyproject.toml",
        "poetry.lock",
    ]

    for item in src_files:
        src_path = Path(item)
        if not src_path.exists():
            print_warning(f"Skipping {item} (not found)")
            continue

        dest_path = backend_output / item
        if src_path.is_dir():
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dest_path)

    print_success("Backend source copied")

    # Install dependencies
    print("\nInstalling backend dependencies...")
    if not run_command(["poetry", "install", "--only", "main"], cwd=backend_output):
        print_error("Failed to install dependencies")
        return False

    print_success("Backend built successfully")
    return True


def package_database(output_dir: Path) -> bool:
    """Package empty database with migrations.

    Args:
        output_dir: Directory for build output

    Returns:
        bool: True if packaging succeeded
    """
    print_step("Packaging Database")

    db_output = output_dir / "database"
    db_output.mkdir(parents=True, exist_ok=True)

    # Copy migration scripts
    migrations_src = Path("alembic")
    if migrations_src.exists():
        migrations_dest = db_output / "migrations"
        shutil.copytree(migrations_src, migrations_dest, dirs_exist_ok=True)
        print_success("Database migrations packaged")

    # Create empty database directory
    (db_output / "data").mkdir(exist_ok=True)
    print_success("Database structure created")

    return True


def create_config_templates(output_dir: Path) -> bool:
    """Create configuration file templates.

    Args:
        output_dir: Directory for build output

    Returns:
        bool: True if creation succeeded
    """
    print_step("Creating Configuration Templates")

    config_output = output_dir / "config"
    config_output.mkdir(parents=True, exist_ok=True)

    # Create .env.example
    env_example = """# TEP Configuration File
# Copy this file to .env and customize for your environment

# Application Environment (development, production, test)
ENVIRONMENT=production

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Backend Server Port
BACKEND_PORT=8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:4200

# Root User Password (CHANGE THIS!)
ROOT_PASSWORD=change_this_secure_password

# Database URL
DATABASE_URL=sqlite:///data/tep.sqlite
"""

    (config_output / ".env.example").write_text(env_example)
    print_success("Configuration templates created")

    return True


def create_scripts(output_dir: Path) -> bool:
    """Copy utility scripts to output.

    Args:
        output_dir: Directory for build output

    Returns:
        bool: True if copy succeeded
    """
    print_step("Copying Utility Scripts")

    scripts_output = output_dir / "scripts"
    scripts_output.mkdir(parents=True, exist_ok=True)

    scripts_to_copy = [
        "scripts/backup_database.py",
        "tools/license_generator.py",
    ]

    for script in scripts_to_copy:
        script_path = Path(script)
        if script_path.exists():
            shutil.copy2(script_path, scripts_output / script_path.name)
            print_success(f"Copied: {script_path.name}")
        else:
            print_warning(f"Script not found: {script}")

    return True


def create_documentation(output_dir: Path, version: str) -> bool:
    """Copy documentation to output.

    Args:
        output_dir: Directory for build output
        version: Version string

    Returns:
        bool: True if copy succeeded
    """
    print_step("Copying Documentation")

    docs_output = output_dir / "docs"
    docs_output.mkdir(parents=True, exist_ok=True)

    docs_to_copy = [
        "README.md",
        "DEPLOYMENT.md",
        "TODO.md",
    ]

    for doc in docs_to_copy:
        doc_path = Path(doc)
        if doc_path.exists():
            shutil.copy2(doc_path, docs_output / doc_path.name)
            print_success(f"Copied: {doc_path.name}")
        else:
            print_warning(f"Documentation not found: {doc}")

    # Create version file
    version_info = {
        "version": version,
        "build_date": datetime.now().isoformat(),
        "python_version": sys.version.split()[0],
    }

    (docs_output / "VERSION.json").write_text(
        json.dumps(version_info, indent=2)
    )
    print_success("Version file created")

    return True


def create_archive(output_dir: Path, version: str) -> bool:
    """Create zip archive of the release.

    Args:
        output_dir: Directory containing build output
        version: Version string

    Returns:
        bool: True if archive created successfully
    """
    print_step("Creating Release Archive")

    archive_name = f"TEP-{version}"
    archive_path = Path("releases") / archive_name

    # Create releases directory
    Path("releases").mkdir(exist_ok=True)

    # Create archive
    print(f"Creating archive: {archive_path}.zip")
    shutil.make_archive(str(archive_path), 'zip', output_dir)

    archive_size_mb = Path(f"{archive_path}.zip").stat().st_size / (1024 * 1024)
    print_success(f"Archive created: {archive_path}.zip ({archive_size_mb:.2f} MB)")

    return True


def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(
        description="TEP Release Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script performs the following steps:
  1. Checks prerequisites (poetry, node, npm)
  2. Runs all tests (backend + frontend)
  3. Builds frontend production bundle
  4. Packages backend with dependencies
  5. Prepares database and migrations
  6. Creates configuration templates
  7. Copies utility scripts and documentation
  8. Creates release archive

Example:
  python build_release.py --version 1.0.0
        """
    )

    parser.add_argument(
        "--version",
        required=True,
        help="Version number for this release (e.g., 1.0.0)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build"),
        help="Build output directory (default: build)"
    )

    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests (not recommended)"
    )

    parser.add_argument(
        "--skip-archive",
        action="store_true",
        help="Skip creating zip archive"
    )

    args = parser.parse_args()

    print(f"{Colors.HEADER}")
    print("=" * 60)
    print(f"TEP Release Builder v{args.version}")
    print("=" * 60)
    print(f"{Colors.ENDC}")

    try:
        # Check prerequisites
        if not check_prerequisites():
            print_error("Prerequisites check failed")
            return 1

        # Run tests
        if not args.skip_tests:
            if not run_tests():
                print_error("Tests failed - aborting build")
                return 1
        else:
            print_warning("Skipping tests (--skip-tests)")

        # Create output directory
        output_dir = args.output_dir / f"TEP-{args.version}"
        if output_dir.exists():
            print_warning(f"Output directory exists, removing: {output_dir}")
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)

        # Build steps
        steps = [
            ("Frontend", lambda: build_frontend(output_dir)),
            ("Backend", lambda: build_backend(output_dir)),
            ("Database", lambda: package_database(output_dir)),
            ("Configuration", lambda: create_config_templates(output_dir)),
            ("Scripts", lambda: create_scripts(output_dir)),
            ("Documentation", lambda: create_documentation(output_dir, args.version)),
        ]

        for step_name, step_func in steps:
            if not step_func():
                print_error(f"{step_name} step failed")
                return 1

        # Create archive
        if not args.skip_archive:
            if not create_archive(output_dir, args.version):
                print_error("Archive creation failed")
                return 1
        else:
            print_warning("Skipping archive creation (--skip-archive)")

        # Success!
        print(f"\n{Colors.OKGREEN}")
        print("=" * 60)
        print(f"✓ Build completed successfully!")
        print(f"  Version: {args.version}")
        print(f"  Output: {output_dir}")
        if not args.skip_archive:
            print(f"  Archive: releases/TEP-{args.version}.zip")
        print("=" * 60)
        print(f"{Colors.ENDC}")

        return 0

    except KeyboardInterrupt:
        print_error("\nBuild interrupted by user")
        return 130
    except Exception as e:
        print_error(f"Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
