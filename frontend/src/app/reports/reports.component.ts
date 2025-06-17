import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
} from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatTableModule } from "@angular/material/table";
import { MatTabsModule } from "@angular/material/tabs";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";

interface ReportData {
  employee_name: string;
  badge_number: string;
  department: string;
  total_hours: number;
  regular_hours: number;
  overtime_hours: number;
  days_worked: number;
  avg_daily_hours: number;
}

@Component({
  selector: "app-reports",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTableModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  templateUrl: "./reports.component.html",
  styleUrl: "./reports.component.scss",
})
export class ReportsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);

  reportForm: FormGroup;
  isLoading = false;
  reportData: ReportData[] = [];
  selectedTabIndex = 0;

  holidayGroups = [
    { value: "", label: "All Holiday Groups" },
    { value: "us-federal", label: "US Federal Holidays" },
    { value: "manufacturing", label: "Manufacturing Holidays" },
    { value: "international", label: "International Holidays" },
  ];

  displayedColumns: string[] = [
    "employee_name",
    "badge_number",
    "department",
    "total_hours",
    "regular_hours",
    "overtime_hours",
    "days_worked",
    "avg_daily_hours",
  ];

  reportTypes = [
    { value: "timesheet", label: "Timesheet Report" },
    { value: "attendance", label: "Attendance Summary" },
    { value: "overtime", label: "Overtime Report" },
    { value: "department", label: "Department Summary" },
    { value: "payroll", label: "Payroll Export" },
  ];

  constructor() {
    this.reportForm = this.fb.group({
      reportType: ["timesheet"],
      dateRange: this.fb.group({
        start: [this.getLastWeekStart()],
        end: [new Date()],
      }),
      department: [""],
      employee: [""],
      holidayGroup: [""],
      format: ["html"],
    });
  }

  ngOnInit() {
    this.generateSampleReport();
  }

  generateReport() {
    this.isLoading = true;
    const formValue = this.reportForm.value;

    setTimeout(() => {
      this.generateSampleReport();
      this.isLoading = false;
      this.showSnackBar(
        `${this.getReportTypeLabel(formValue.reportType)} generated successfully`,
        "success",
      );
    }, 1500);
  }

  exportReport(format: "pdf" | "excel" | "csv") {
    this.showSnackBar(`Exporting report as ${format.toUpperCase()}...`, "info");

    // Simulate export
    setTimeout(() => {
      this.showSnackBar(
        `Report exported as ${format.toUpperCase()} successfully`,
        "success",
      );
    }, 2000);
  }

  getReportTypeLabel(value: string): string {
    const type = this.reportTypes.find((t) => t.value === value);
    return type ? type.label : value;
  }

  getTotalHours(): number {
    return this.reportData.reduce((sum, item) => sum + item.total_hours, 0);
  }

  getTotalEmployees(): number {
    return this.reportData.length;
  }

  getAverageHours(): number {
    if (this.reportData.length === 0) return 0;
    return this.getTotalHours() / this.reportData.length;
  }

  getTotalOvertimeHours(): number {
    return this.reportData.reduce((sum, item) => sum + item.overtime_hours, 0);
  }

  private getLastWeekStart(): Date {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date;
  }

  private generateSampleReport() {
    this.reportData = [
      {
        employee_name: "John Doe",
        badge_number: "EMP001",
        department: "IT",
        total_hours: 42.5,
        regular_hours: 40.0,
        overtime_hours: 2.5,
        days_worked: 5,
        avg_daily_hours: 8.5,
      },
      {
        employee_name: "Jane Smith",
        badge_number: "EMP002",
        department: "HR",
        total_hours: 40.0,
        regular_hours: 40.0,
        overtime_hours: 0.0,
        days_worked: 5,
        avg_daily_hours: 8.0,
      },
      {
        employee_name: "Mike Johnson",
        badge_number: "EMP003",
        department: "Manufacturing",
        total_hours: 45.0,
        regular_hours: 40.0,
        overtime_hours: 5.0,
        days_worked: 5,
        avg_daily_hours: 9.0,
      },
      {
        employee_name: "Sarah Wilson",
        badge_number: "EMP004",
        department: "Sales",
        total_hours: 38.5,
        regular_hours: 38.5,
        overtime_hours: 0.0,
        days_worked: 5,
        avg_daily_hours: 7.7,
      },
      {
        employee_name: "David Brown",
        badge_number: "EMP005",
        department: "Manufacturing",
        total_hours: 44.0,
        regular_hours: 40.0,
        overtime_hours: 4.0,
        days_worked: 5,
        avg_daily_hours: 8.8,
      },
    ];
  }

  private showSnackBar(
    message: string,
    type: "success" | "error" | "info" = "info",
  ) {
    this.snackBar.open(message, "Close", {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
