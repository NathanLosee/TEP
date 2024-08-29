"""Primary driver for application."""

from contextlib import asynccontextmanager
from http import HTTPStatus
from importlib import import_module
from pathlib import Path
import json
from sys import gettrace
from typing import Annotated

from fastapi.exceptions import RequestValidationError
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask
from starlette.types import Message
from src.config import Settings, get_settings
from src.database import cleanup_tables, get_db
from src.logger.app_logger import get_logger
from src.logger.formatter import CustomFormatter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Define actions to take in initializing and closing of application.

    Args:
        app (FastAPI): The FastAPI application object.

    """
    try:
        yield
    finally:
        db = next(get_db())
        cleanup_tables(db)


app = FastAPI(lifespan=lifespan)


AppSettings = Annotated[Settings, Depends(get_settings)]

formatter = CustomFormatter("%(asctime)s")
logger = get_logger(__name__, formatter, log_level=AppSettings().LOG_LEVEL)
status_reasons = {x.value: x.name for x in list(HTTPStatus)}
ignored_endpoints = ["/docs", "/redoc", "/openapi.json"]


async def set_request_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    request._receive = receive


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


def get_extra_info(
    request: Request, req_body, response: Response, res_body
) -> dict:
    """Produce and return extra information about a given request and response.

    Args:
        request (Request): The incoming request.
        req_body: Body of the incoming request.
        response (Response): The outgoing response.
        res_body: Body of the outgoing response.

    Returns:
        dict: The extra info gathered.

    """
    req_obj = {
        "method": request.method,
        "path": request.url.path,
        "query_params": (
            request.query_params._dict
            if len(request.query_params._list) > 0
            else {}
        ),
        "body": json.loads(req_body.decode()) if req_body != b"" else {},
    }

    if (
        response.status_code >= 400 or gettrace()
    ) and response.status_code != 204:
        res_obj = {
            "status_code": response.status_code,
            "status": status_reasons[response.status_code],
            "data": json.loads(res_body.decode()),
        }
    else:
        res_obj = {
            "status_code": response.status_code,
            "status": status_reasons[response.status_code],
        }

    return {"request": req_obj, "response": res_obj}


def write_log_data(request: Request, req_body, response: Response, res_body):
    """The the log for an incoming request.

    Args:
        request (Request): The incoming request
        req_body: Body of the request.
        response (Response): The outgoing response.
        res_body: Body of the response.

    """
    extra_info = get_extra_info(request, req_body, response, res_body)
    logger.info(
        request.method + " " + request.url.path,
        extra={"extra_info": extra_info},
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

    task = BackgroundTask(
        write_log_data, request, req_body, response, res_body
    )

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
    return {"message": "Welcome to the Python Super Health API project!"}


import_routers()
