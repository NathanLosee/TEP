"""Module for health check and metrics endpoints."""

import time
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import get_db
from src.services import is_license_activated

router = APIRouter(tags=["health"])

# Application start time (set on module import during startup)
_start_time: float = time.time()

# In-memory metrics store
_metrics_lock = Lock()
_request_counts: dict[str, int] = defaultdict(int)
_error_counts: dict[int, int] = defaultdict(int)
_response_times: list[float] = []
_total_requests: int = 0

# Max response times to keep in memory (rolling window)
_MAX_RESPONSE_TIMES = 1000


def record_request(
    method: str, path: str,
    status_code: int, duration_ms: float,
):
    """Record metrics for a completed request.

    Args:
        method: HTTP method (GET, POST, etc.).
        path: Request path.
        status_code: Response status code.
        duration_ms: Request duration in milliseconds.

    """
    global _total_requests

    with _metrics_lock:
        _total_requests += 1
        _request_counts[f"{method} {path}"] += 1

        if status_code >= 400:
            _error_counts[status_code] += 1

        _response_times.append(duration_ms)
        if len(_response_times) > _MAX_RESPONSE_TIMES:
            _response_times.pop(0)


def _get_uptime_seconds() -> float:
    return time.time() - _start_time


@router.get("/health", status_code=200)
def health_check(db: Session = Depends(get_db)):
    """Application health check.

    Returns database connectivity, license status, and uptime.

    """
    # Check database connectivity
    db_healthy = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_healthy = False

    uptime = _get_uptime_seconds()
    healthy = db_healthy

    from src.main import app

    return {
        "status": "healthy" if healthy else "unhealthy",
        "version": app.version,
        "database": "connected" if db_healthy else "disconnected",
        "license_active": is_license_activated,
        "uptime_seconds": round(uptime, 1),
    }


@router.get("/metrics", status_code=200)
def get_metrics():
    """Application metrics.

    Returns request counts, error rates, and response time statistics.

    """
    with _metrics_lock:
        avg_response_time = (
            round(sum(_response_times) / len(_response_times), 2)
            if _response_times
            else 0.0
        )
        p95_response_time = (
            round(sorted(_response_times)[int(len(_response_times) * 0.95)], 2)
            if _response_times
            else 0.0
        )
        max_response_time = (
            round(max(_response_times), 2) if _response_times else 0.0
        )

        total_errors = sum(_error_counts.values())
        error_rate = (
            round(total_errors / _total_requests * 100, 2)
            if _total_requests > 0
            else 0.0
        )

        return {
            "total_requests": _total_requests,
            "error_rate_percent": error_rate,
            "response_time_ms": {
                "avg": avg_response_time,
                "p95": p95_response_time,
                "max": max_response_time,
            },
            "errors_by_status": dict(_error_counts),
            "uptime_seconds": round(_get_uptime_seconds(), 1),
        }
