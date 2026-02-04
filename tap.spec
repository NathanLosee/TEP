# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for TAP Backend.

This spec file configures PyInstaller to bundle the TAP backend
into a standalone Windows executable.

Usage:
    pyinstaller tap.spec
    # Or via build_release.py:
    python scripts/build_release.py --version 1.0.0

The resulting executable will be in dist/tap/tap.exe
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)

# Collect all route modules explicitly since they're dynamically imported
hidden_imports = [
    # Core modules
    'src.config',
    'src.database',
    'src.services',
    'src.models',
    # Route modules (dynamically imported in main.py)
    'src.auth_role.routes',
    'src.auth_role.repository',
    'src.auth_role.models',
    'src.auth_role.schemas',
    'src.user.routes',
    'src.user.repository',
    'src.user.models',
    'src.user.schemas',
    'src.employee.routes',
    'src.employee.repository',
    'src.employee.models',
    'src.employee.schemas',
    'src.department.routes',
    'src.department.repository',
    'src.department.models',
    'src.department.schemas',
    'src.org_unit.routes',
    'src.org_unit.repository',
    'src.org_unit.models',
    'src.org_unit.schemas',
    'src.holiday_group.routes',
    'src.holiday_group.repository',
    'src.holiday_group.models',
    'src.holiday_group.schemas',
    'src.timeclock.routes',
    'src.timeclock.repository',
    'src.timeclock.models',
    'src.timeclock.schemas',
    'src.registered_browser.routes',
    'src.registered_browser.repository',
    'src.registered_browser.models',
    'src.registered_browser.schemas',
    'src.license.routes',
    'src.license.repository',
    'src.license.models',
    'src.license.schemas',
    'src.license.key_generator',
    'src.event_log.routes',
    'src.event_log.repository',
    'src.event_log.models',
    'src.event_log.schemas',
    'src.system_settings.routes',
    'src.system_settings.repository',
    'src.system_settings.models',
    'src.system_settings.schemas',
    'src.report.routes',
    'src.report.service',
    'src.report.schemas',
    'src.report.pdf_export',
    'src.updater.routes',
    'src.updater.service',
    'src.updater.schemas',
    'src.updater.constants',
    # Logger
    'src.logger.app_logger',
    'src.logger.formatter',
    # FastAPI and dependencies
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'pydantic',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'alembic',
    # Cryptography
    'cryptography',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.asymmetric.ed25519',
    'bcrypt',
    'jwt',
    # Other dependencies
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.colors',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'reportlab.platypus',
    'machineid',
    'httpx',
    'email_validator',
    # PIL for reportlab image handling
    'PIL',
    'PIL.Image',
    # Static file serving
    'aiofiles',
]

# Data files to include
datas = [
    # Source code (needed for dynamic router imports in main.py)
    ('src', 'src'),
    # Alembic migrations
    ('alembic', 'alembic'),
    ('alembic.ini', '.'),
    # Word list for license key conversion
    ('words.txt', '.'),
    # Update helper script
    ('scripts/apply-update.ps1', 'scripts'),
]

# Binary files (none specific for this project)
binaries = []

a = Analysis(
    ['run_server.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test modules
        'pytest',
        'pytest_cov',
        'bandit',
        'safety',
        # Exclude unused modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console app for logging output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='assets/tap.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tap',
)
