"""Primary driver for application."""

import asyncio
import sys
from contextlib import asynccontextmanager
from http import HTTPStatus
from importlib import import_module
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask
from starlette.types import Message

from src.config import Settings
from src.logger.app_logger import get_logger
from src.logger.formatter import CustomFormatter
from src.scheduler import periodic_cleanup
from src.services import (
    clear_database,
    create_root_user_if_not_exists,
    generate_dummy_data,
    load_keys,
    validate_license_on_startup,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: Start background scheduler
    cleanup_task = asyncio.create_task(periodic_cleanup())

    yield

    # Shutdown: Cancel background tasks
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)
settings = Settings()
formatter = CustomFormatter("%(asctime)s")
logger = get_logger(__name__, formatter, log_level=settings.LOG_LEVEL)
status_reasons = {x.value: x.name for x in list(HTTPStatus)}
ignored_endpoints = ["/docs", "/redoc", "/openapi.json"]


def import_routers():
    """Dynamically imports all routers in domain directories.

    When running as a PyInstaller bundle, we use explicit module names
    since filesystem iteration doesn't work with bundled resources.
    """
    # Explicit list of route modules for PyInstaller compatibility
    route_modules = [
        "src.auth_role.routes",
        "src.department.routes",
        "src.employee.routes",
        "src.event_log.routes",
        "src.holiday_group.routes",
        "src.license.routes",
        "src.org_unit.routes",
        "src.registered_browser.routes",
        "src.report.routes",
        "src.system_settings.routes",
        "src.timeclock.routes",
        "src.user.routes",
    ]

    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Use explicit module list
        for module_name in route_modules:
            try:
                routes_module = import_module(module_name)
                router = getattr(routes_module, "router", None)
                if router:
                    app.include_router(router)
            except ImportError as e:
                logger.warning(f"Could not import {module_name}: {e}")
    else:
        # Dynamic discovery for development
        src_path = Path("src")
        for domain_path in src_path.iterdir():
            if (
                domain_path.is_dir()
                and domain_path.name != "logger"
                and not domain_path.name.startswith("__")
            ):
                routes_path = Path(f"{src_path.name}.{domain_path.name}.routes")
                routes_module = import_module(str(routes_path))
                router = getattr(routes_module, "router", None)
                app.include_router(router)


def write_log_data(request: Request, response: Response):
    """The log for an incoming request.

    Args:
        request (Request): The incoming request
        response (Response): The outgoing response.

    """
    logger.info(
        request.method + " " + request.url.path,
        extra={
            "extra_info": {
                "status_code": response.status_code,
                "status": status_reasons[response.status_code],
            }
        },
    )


async def set_request_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    request._receive = receive


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """Log incoming request to the application.

    Args:
        request (Request): The incoming request.
        call_next: The next function to handle the request.

    Returns:
        Response: The response to the request.

    """
    if request.url.path in ignored_endpoints:
        return await call_next(request)

    req_body = await request.body()
    await set_request_body(request, req_body)
    response = await call_next(request)

    res_body = b""
    async for chunk in response.body_iterator:
        res_body += chunk

    task = BackgroundTask(write_log_data, request, response)

    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=task,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Capture, log, and modify the status code of a RequestValidationError.

    Args:
        request (Request): The request generating the RequestValidationError.
        exc (RequestValidationError): The validation error captured.

    Returns:
        JSONResponse: The modified response.

    """
    task = BackgroundTask(logger.exception, exc)
    return JSONResponse(
        str(exc), status_code=status.HTTP_400_BAD_REQUEST, background=task
    )


@app.exception_handler(Exception)
async def system_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Capture and log an exception.

    Args:
        request (Request): The request generating the exception.
        exc (Exception): The exception captured.

    Returns:
        JSONResponse: The modified response.

    """
    task = BackgroundTask(logger.exception, exc)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
        background=task,
    )


@app.get("/", status_code=status.HTTP_200_OK, summary="Welcome")
def root() -> dict:
    """Welcome route for the application.

    Returns:
        dict: The JSON welcome message for the application.

    """
    return {"message": "Welcome to Timeclock and Employee Payroll!"}


import_routers()
load_keys()
if settings.ENVIRONMENT == "development":
    clear_database()
create_root_user_if_not_exists()
if settings.ENVIRONMENT == "development":
    generate_dummy_data()
validate_license_on_startup()


def setup_static_files():
    """Set up static file serving for the Angular frontend.

    In production, serves the built Angular app from the frontend directory.
    The frontend directory location depends on whether running as PyInstaller
    bundle or from source.
    """
    # Determine the base path
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle - get the directory containing the executable
        # sys.executable points to tep.exe in the backend folder
        # Frontend is a sibling folder at the same level as backend
        exe_dir = Path(sys.executable).parent  # backend/
        base_path = exe_dir.parent  # TEP-x.x.x/ (parent of backend)
    else:
        # Running from source - check for built frontend
        base_path = Path(__file__).parent.parent

    # Look for frontend in multiple possible locations
    frontend_paths = [
        base_path / "frontend",              # Release structure: TEP-x.x.x/frontend/
        base_path / "frontend" / "browser",  # Alternative with browser subfolder
        base_path / "frontend" / "dist" / "tep-frontend" / "browser",  # Dev build location
    ]

    frontend_path = None
    for path in frontend_paths:
        if path.exists() and (path / "index.html").exists():
            frontend_path = path
            break

    if frontend_path is None:
        logger.info("Frontend static files not found - API only mode")
        return

    logger.info(f"Serving frontend from: {frontend_path}")

    # Mount static files for assets (JS, CSS, images, etc.)
    app.mount(
        "/assets",
        StaticFiles(directory=frontend_path / "assets" if (frontend_path / "assets").exists() else frontend_path),
        name="assets"
    )

    # Serve other static files (favicon, etc.)
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        favicon_path = frontend_path / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        return Response(status_code=404)

    # Serve Angular's static files (JS bundles, CSS)
    for pattern in ["*.js", "*.css", "*.woff2", "*.woff", "*.ttf", "*.svg", "*.png", "*.jpg"]:
        for static_file in frontend_path.glob(pattern):
            file_name = static_file.name

            @app.get(f"/{file_name}", include_in_schema=False)
            async def serve_static(file_path=static_file):
                return FileResponse(file_path)

    # Catch-all route for Angular's client-side routing
    # This must be registered LAST to not interfere with API routes
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_angular(full_path: str):
        # Don't serve index.html for API routes
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
            return Response(status_code=404)

        # Check if it's a request for a static file
        requested_file = frontend_path / full_path
        if requested_file.exists() and requested_file.is_file():
            return FileResponse(requested_file)

        # Otherwise, serve index.html for Angular routing
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return Response(status_code=404)


# Set up static files for production
if settings.ENVIRONMENT != "development":
    setup_static_files()
