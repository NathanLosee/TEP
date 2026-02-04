"""Module for generating PDF reports from report data."""

from io import BytesIO
from typing import Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.report.constants import (
    DETAIL_LEVEL_DETAILED,
    DETAIL_LEVEL_EMPLOYEE_SUMMARY,
    DETAIL_LEVEL_SUMMARY,
    REPORT_TYPE_DEPARTMENT,
    REPORT_TYPE_ORG_UNIT,
)
from src.report.schemas import EmployeeReportData, ReportResponse


def generate_pdf_report(
    report: ReportResponse,
    detail_level: str = DETAIL_LEVEL_SUMMARY,
    logo_data: Optional[Tuple[bytes, str, str]] = None,
    company_name: str = "TAP Timeclock",
) -> BytesIO:
    """Generate a PDF report from report data.

    Args:
        report (ReportResponse): The report data.
        detail_level (str): Level of detail to include.
        logo_data (tuple): Optional tuple of (logo_bytes, mime_type, filename).
        company_name (str): Company name for the header.

    Returns:
        BytesIO: PDF file buffer.

    """
    buffer = BytesIO()

    # Create logo image reader if logo data provided
    logo_image = None
    if logo_data and logo_data[0]:
        try:
            logo_bytes, mime_type, _ = logo_data
            logo_image = ImageReader(BytesIO(logo_bytes))
        except Exception:
            logo_image = None

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Container for document elements
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1976d2"),
        spaceAfter=12,
        alignment=1,  # Center alignment
    )

    elements.append(
        Paragraph(f"{company_name} - Timeclock Report", title_style)
    )

    # Add department/org unit subtitle if applicable
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#424242"),
        spaceAfter=8,
        alignment=1,
    )

    if report.report_type == REPORT_TYPE_DEPARTMENT and report.filter_name:
        elements.append(
            Paragraph(f"Department: {report.filter_name}", subtitle_style)
        )
    elif report.report_type == REPORT_TYPE_ORG_UNIT and report.filter_name:
        elements.append(
            Paragraph(
                f"Organizational Unit: {report.filter_name}", subtitle_style
            )
        )

    # Report metadata
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"], alignment=1, fontSize=10
    )
    elements.append(
        Paragraph(
            f"Period: {report.start_date} to {report.end_date}",
            meta_style,
        )
    )
    elements.append(
        Paragraph(
            f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}",
            meta_style,
        )
    )
    elements.append(Spacer(1, 0.5 * inch))

    # Determine if this is a single employee report
    is_single_employee = len(report.employees) == 1

    # Summary section - skip for single employee reports
    if not is_single_employee:
        _add_summary_section(elements, report, styles)

    # Employee sections (if detail level >= employee_summary)
    if detail_level in [DETAIL_LEVEL_EMPLOYEE_SUMMARY, DETAIL_LEVEL_DETAILED]:
        for idx, employee_data in enumerate(report.employees):
            # Create a list of elements to keep together for each employee
            employee_elements = []

            # Add employee summary
            _add_employee_summary_section(
                employee_elements, employee_data, styles
            )

            # If detailed, add time entries on same page after summary
            if detail_level == DETAIL_LEVEL_DETAILED:
                employee_elements.append(Spacer(1, 0.3 * inch))
                _add_employee_detailed_section(
                    employee_elements, employee_data, report, styles
                )

            # For single employee, no page break needed before content
            # For multiple employees, add page break before
            # each employee section
            if not is_single_employee:
                elements.append(PageBreak())

            # Use KeepTogether to try to keep summary and details on same page
            elements.append(KeepTogether(employee_elements))

    # Build PDF with custom page drawing for watermark
    def add_watermark(canvas, doc):
        """Add watermark logo to each page."""
        if logo_image:
            canvas.saveState()
            # Get page dimensions
            page_width, page_height = letter

            # Calculate watermark size (larger - 6 inches)
            watermark_size = 6 * inch

            # Center position
            x = (page_width - watermark_size) / 2
            y = (page_height - watermark_size) / 2

            # Set transparency (very light)
            canvas.setFillAlpha(0.08)

            # Draw the image
            try:
                canvas.drawImage(
                    logo_image,
                    x,
                    y,
                    width=watermark_size,
                    height=watermark_size,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                pass  # Skip watermark if image fails

            canvas.restoreState()

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    # Reset buffer position to beginning and return
    buffer.seek(0)
    return buffer


def _add_summary_section(elements, report: ReportResponse, styles):
    """Add summary section to PDF.

    Args:
        elements (list): Document elements list.
        report (ReportResponse): Report data.
        styles: ReportLab styles.

    """
    elements.append(
        Paragraph(
            "Summary",
            ParagraphStyle("SectionTitle", parent=styles["Heading2"]),
        )
    )
    elements.append(Spacer(1, 0.2 * inch))

    # Summary table data
    summary_data = [
        [
            "Employee",
            "Badge #",
            "Total Hours",
            "Regular",
            "Overtime",
            "Holiday",
            "Days Worked",
        ]
    ]

    # Handle empty employee list
    if not report.employees:
        summary_data.append(
            ["No data", "", "0.00", "0.00", "0.00", "0.00", "0"]
        )
    else:
        for emp_data in report.employees:
            summary_data.append(
                [
                    f"{emp_data.first_name} {emp_data.last_name}",
                    emp_data.badge_number,
                    f"{emp_data.summary.total_hours:.2f}",
                    f"{emp_data.summary.regular_hours:.2f}",
                    f"{emp_data.summary.overtime_hours:.2f}",
                    f"{emp_data.summary.holiday_hours:.2f}",
                    str(emp_data.summary.days_worked),
                ]
            )

    # Calculate totals
    total_hours = sum(e.summary.total_hours for e in report.employees)
    total_regular = sum(e.summary.regular_hours for e in report.employees)
    total_overtime = sum(e.summary.overtime_hours for e in report.employees)
    total_holiday = sum(e.summary.holiday_hours for e in report.employees)

    summary_data.append(
        [
            "TOTAL",
            "",
            f"{total_hours:.2f}",
            f"{total_regular:.2f}",
            f"{total_overtime:.2f}",
            f"{total_holiday:.2f}",
            "",
        ]
    )

    # Create table
    table = Table(
        summary_data,
        colWidths=[
            1.5 * inch,
            0.9 * inch,
            0.9 * inch,
            0.8 * inch,
            0.8 * inch,
            0.8 * inch,
            1 * inch,
        ],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e3f2fd")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(table)


def _add_employee_summary_section(
    elements, employee_data: EmployeeReportData, styles
):
    """Add employee summary section to PDF.

    Args:
        elements (list): Document elements list.
        employee_data (EmployeeReportData): Employee report data.
        styles: ReportLab styles.

    """
    section_title = ParagraphStyle(
        "EmployeeSection",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1976d2"),
    )
    elements.append(
        Paragraph(
            f"Employee: {employee_data.first_name} "
            f"{employee_data.last_name} "
            f"({employee_data.badge_number})",
            section_title,
        )
    )
    elements.append(Spacer(1, 0.2 * inch))

    # Employee summary details
    summary_items = [
        ["Metric", "Value"],
        ["Total Hours", f"{employee_data.summary.total_hours:.2f}"],
        ["Regular Hours", f"{employee_data.summary.regular_hours:.2f}"],
        ["Overtime Hours", f"{employee_data.summary.overtime_hours:.2f}"],
        ["Holiday Hours", f"{employee_data.summary.holiday_hours:.2f}"],
        ["Days Worked", str(employee_data.summary.days_worked)],
    ]

    summary_table = Table(summary_items, colWidths=[2.5 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(summary_table)


def _add_employee_detailed_section(
    elements,
    employee_data: EmployeeReportData,
    report: ReportResponse,
    styles,
):
    """Add employee detailed time entries section to PDF.

    Args:
        elements (list): Document elements list.
        employee_data (EmployeeReportData): Employee report data.
        report (ReportResponse): Full report data.
        styles: ReportLab styles.

    """
    section_title = ParagraphStyle(
        "DetailedSection",
        parent=styles["Heading3"],
        textColor=colors.HexColor("#424242"),
    )
    elements.append(
        Paragraph(
            "Time Entries",
            section_title,
        )
    )
    elements.append(Spacer(1, 0.15 * inch))

    # Process each month
    for month in employee_data.months:
        month_title = ParagraphStyle(
            "MonthTitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#1976d2"),
            fontName="Helvetica-Bold",
        )
        elements.append(
            Paragraph(
                f"{month.year}-{month.month:02d} "
                f"(Total: {month.total_hours:.2f} hours)",
                month_title,
            )
        )
        elements.append(Spacer(1, 0.08 * inch))

        # Table for this month
        month_data = [["Date", "Clock In", "Clock Out", "Hours"]]

        for day in month.days:
            for period in day.periods:
                clock_in_str = period.clock_in.strftime("%Y-%m-%d %H:%M")
                clock_out_str = (
                    period.clock_out.strftime("%Y-%m-%d %H:%M")
                    if period.clock_out
                    else "Not clocked out"
                )
                month_data.append(
                    [
                        period.clock_in.strftime("%Y-%m-%d"),
                        clock_in_str,
                        clock_out_str,
                        f"{period.hours:.2f}",
                    ]
                )

        month_table = Table(
            month_data,
            colWidths=[1.2 * inch, 1.8 * inch, 1.8 * inch, 0.8 * inch],
        )
        month_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#64b5f6"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(month_table)
        elements.append(Spacer(1, 0.15 * inch))
