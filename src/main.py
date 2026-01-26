"""Primary driver for application."""

from http import HTTPStatus
from importlib import import_module
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask
from starlette.types import Message

from src.config import Settings
from src.logger.app_logger import get_logger
from src.logger.formatter import CustomFormatter
from src.services import (
    clear_database,
    create_root_user_if_not_exists,
    generate_dummy_data,
    load_keys,
    validate_license_on_startup,
)

app = FastAPI()
settings = Settings()
formatter = CustomFormatter("%(asctime)s")
logger = get_logger(__name__, formatter, log_level=settings.LOG_LEVEL)
status_reasons = {x.value: x.name for x in list(HTTPStatus)}
ignored_endpoints = ["/docs", "/redoc", "/openapi.json"]


def import_routers():
    """Dynamically imports all routers in domain directories."""
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
