"""Module defining FastAPI routes for report-related operations."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.params import Security
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.report.constants import BASE_URL
from src.report.pdf_export import generate_pdf_report
from src.report.schemas import ReportRequest, ReportResponse
from src.report.service import generate_report
from src.services import requires_license, requires_permission
from src.system_settings.repository import get_logo, get_settings

router = APIRouter(prefix=BASE_URL, tags=["Reports"])


@router.post("", response_model=ReportResponse)
def create_report(
    request: ReportRequest,
    db: Annotated[Session, Depends(get_db)],
    caller_badge: str = Security(requires_permission, scopes=["report.read"]),
    _: None = Depends(requires_license),
) -> ReportResponse:
    """Generate a timeclock report.

    Args:
        request (ReportRequest): Report generation parameters.
        db (Session): Database session for the current request.

    Returns:
        ReportResponse: Complete report data.

    """
    return generate_report(
        start_date=request.start_date,
        end_date=request.end_date,
        db=db,
        employee_id=request.employee_id,
        department_id=request.department_id,
        org_unit_id=request.org_unit_id,
    )


@router.get("/pdf")
def export_report_pdf(
    start_date: Annotated[str, Query(description="Start date (YYYY-MM-DD)")],
    end_date: Annotated[str, Query(description="End date (YYYY-MM-DD)")],
    detail_level: Annotated[
        str,
        Query(description="Detail level: summary, employee_summary, detailed"),
    ] = "summary",
    employee_id: Annotated[
        int | None, Query(description="Optional employee ID")
    ] = None,
    department_id: Annotated[
        int | None, Query(description="Optional department ID")
    ] = None,
    org_unit_id: Annotated[
        int | None, Query(description="Optional org unit ID")
    ] = None,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["report.export"]
    ),
    _: None = Depends(requires_license),
):
    """Export timeclock report as PDF.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        detail_level (str): Level of detail (summary, employee_summary,
            detailed).
        employee_id (int): Optional employee ID filter.
        department_id (int): Optional department ID filter.
        org_unit_id (int): Optional org unit ID filter.
        db (Session): Database session.

    Returns:
        StreamingResponse: PDF file stream.

    """
    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Generate report data
    report = generate_report(
        start_date=start,
        end_date=end,
        db=db,
        employee_id=employee_id,
        department_id=department_id,
        org_unit_id=org_unit_id,
    )

    # Get logo and company name for PDF
    logo_data = get_logo(db)
    settings = get_settings(db)
    company_name = settings.company_name if settings else "TAP Timeclock"

    # Generate PDF
    try:
        pdf_buffer = generate_pdf_report(
            report,
            detail_level,
            logo_data=logo_data,
            company_name=company_name,
        )
        pdf_bytes = pdf_buffer.read()

        # Return as Response with proper headers
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    "attachment; filename="
                    f"timeclock_report_{start_date}"
                    f"_to_{end_date}.pdf"
                ),
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as e:
        # Log the real error server-side only
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="Error generating PDF report"
        )
