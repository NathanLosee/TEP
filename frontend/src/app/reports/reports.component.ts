import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatExpansionModule } from "@angular/material/expansion";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { MatTooltipModule } from "@angular/material/tooltip";

import {
  ReportService,
  ReportResponse,
  EmployeeReportData
} from "../../services/report.service";
import { EmployeeService } from "../../services/employee.service";
import { DepartmentService } from "../../services/department.service";
import { OrgUnitService } from "../../services/org-unit.service";

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
    MatExpansionModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTooltipModule,
  ],
  templateUrl: "./reports.component.html",
  styleUrl: "./reports.component.scss",
})
export class ReportsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private reportService = inject(ReportService);
  private employeeService = inject(EmployeeService);
  private departmentService = inject(DepartmentService);
  private orgUnitService = inject(OrgUnitService);

  reportForm: FormGroup;
  isLoading = false;
  reportData: ReportResponse | null = null;

  employees: any[] = [];
  departments: any[] = [];
  orgUnits: any[] = [];

  reportTypes = [
    { value: "all", label: "All Employees" },
    { value: "employee", label: "Individual Employee" },
    { value: "department", label: "Department" },
    { value: "org_unit", label: "Organizational Unit" },
  ];

  detailLevels = [
    { value: "summary", label: "Summary Only" },
    { value: "employee_summary", label: "Summary + Employee Details" },
    { value: "detailed", label: "Full Detailed Report" },
  ];

  // Track expansion state for drill-down
  expandedEmployees: Set<number> = new Set();
  expandedMonths: Map<number, Set<string>> = new Map();
  expandedDays: Map<number, Map<string, Set<string>>> = new Map();

  constructor() {
    this.reportForm = this.fb.group({
      reportType: ["all"],
      dateRange: this.fb.group({
        start: [this.getLastWeekStart(), Validators.required],
        end: [new Date(), Validators.required],
      }),
      employee: [null],
      department: [null],
      orgUnit: [null],
      detailLevel: ["summary"],
    });

    // Subscribe to report type changes to reset filters
    this.reportForm.get("reportType")?.valueChanges.subscribe(() => {
      this.reportForm.patchValue({
        employee: null,
        department: null,
        orgUnit: null,
      });
    });
  }

  ngOnInit() {
    this.loadEmployees();
    this.loadDepartments();
    this.loadOrgUnits();
  }

  loadEmployees() {
    this.employeeService.getEmployees().subscribe({
      next: (data) => {
        this.employees = data;
      },
      error: (error) => {
        console.error("Error loading employees:", error);
        this.showSnackBar("Failed to load employees", "error");
      },
    });
  }

  loadDepartments() {
    this.departmentService.getDepartments().subscribe({
      next: (data) => {
        this.departments = data;
      },
      error: (error) => {
        console.error("Error loading departments:", error);
        this.showSnackBar("Failed to load departments", "error");
      },
    });
  }

  loadOrgUnits() {
    this.orgUnitService.getOrgUnits().subscribe({
      next: (data) => {
        this.orgUnits = data;
      },
      error: (error) => {
        console.error("Error loading org units:", error);
        this.showSnackBar("Failed to load org units", "error");
      },
    });
  }

  generateReport() {
    if (this.reportForm.invalid) {
      this.showSnackBar("Please fill in all required fields", "error");
      return;
    }

    this.isLoading = true;
    const formValue = this.reportForm.value;
    const reportType = formValue.reportType;

    const request = {
      start_date: this.formatDate(formValue.dateRange.start),
      end_date: this.formatDate(formValue.dateRange.end),
      employee_id: reportType === "employee" ? formValue.employee : undefined,
      department_id: reportType === "department" ? formValue.department : undefined,
      org_unit_id: reportType === "org_unit" ? formValue.orgUnit : undefined,
    };

    this.reportService.generateReport(request).subscribe({
      next: (data) => {
        this.reportData = data;
        this.isLoading = false;
        this.expandedEmployees.clear();
        this.expandedMonths.clear();
        this.expandedDays.clear();
        this.showSnackBar("Report generated successfully", "success");
      },
      error: (error) => {
        console.error("Error generating report:", error);
        this.isLoading = false;
        this.showSnackBar("Failed to generate report", "error");
      },
    });
  }

  exportPDF() {
    if (!this.reportData) {
      this.showSnackBar("Please generate a report first", "error");
      return;
    }

    const formValue = this.reportForm.value;
    const reportType = formValue.reportType;

    this.reportService
      .exportPDF(
        this.formatDate(formValue.dateRange.start),
        this.formatDate(formValue.dateRange.end),
        formValue.detailLevel,
        reportType === "employee" ? formValue.employee : undefined,
        reportType === "department" ? formValue.department : undefined,
        reportType === "org_unit" ? formValue.orgUnit : undefined
      )
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = `timeclock_report_${this.formatDate(formValue.dateRange.start)}_to_${this.formatDate(formValue.dateRange.end)}.pdf`;
          link.click();
          window.URL.revokeObjectURL(url);
          this.showSnackBar("PDF exported successfully", "success");
        },
        error: (error) => {
          console.error("Error exporting PDF:", error);
          this.showSnackBar("Failed to export PDF", "error");
        },
      });
  }

  toggleEmployee(employeeId: number) {
    if (this.expandedEmployees.has(employeeId)) {
      this.expandedEmployees.delete(employeeId);
    } else {
      this.expandedEmployees.add(employeeId);
    }
  }

  isEmployeeExpanded(employeeId: number): boolean {
    return this.expandedEmployees.has(employeeId);
  }

  toggleMonth(employeeId: number, monthKey: string) {
    if (!this.expandedMonths.has(employeeId)) {
      this.expandedMonths.set(employeeId, new Set());
    }
    const months = this.expandedMonths.get(employeeId)!;
    if (months.has(monthKey)) {
      months.delete(monthKey);
    } else {
      months.add(monthKey);
    }
  }

  isMonthExpanded(employeeId: number, monthKey: string): boolean {
    return this.expandedMonths.get(employeeId)?.has(monthKey) || false;
  }

  toggleDay(employeeId: number, monthKey: string, dayKey: string) {
    if (!this.expandedDays.has(employeeId)) {
      this.expandedDays.set(employeeId, new Map());
    }
    const employeeDays = this.expandedDays.get(employeeId)!;
    if (!employeeDays.has(monthKey)) {
      employeeDays.set(monthKey, new Set());
    }
    const days = employeeDays.get(monthKey)!;
    if (days.has(dayKey)) {
      days.delete(dayKey);
    } else {
      days.add(dayKey);
    }
  }

  isDayExpanded(employeeId: number, monthKey: string, dayKey: string): boolean {
    return (
      this.expandedDays.get(employeeId)?.get(monthKey)?.has(dayKey) || false
    );
  }

  getMonthKey(month: any): string {
    return `${month.year}-${month.month.toString().padStart(2, "0")}`;
  }

  getTotalHours(): number {
    if (!this.reportData) return 0;
    return this.reportData.employees.reduce(
      (sum, emp) => sum + emp.summary.total_hours,
      0
    );
  }

  getTotalEmployees(): number {
    return this.reportData?.employees.length || 0;
  }

  getAverageHours(): number {
    if (!this.reportData || this.reportData.employees.length === 0) return 0;
    return this.getTotalHours() / this.reportData.employees.length;
  }

  getTotalOvertimeHours(): number {
    if (!this.reportData) return 0;
    return this.reportData.employees.reduce(
      (sum, emp) => sum + emp.summary.overtime_hours,
      0
    );
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  private getLastWeekStart(): Date {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date;
  }

  private showSnackBar(
    message: string,
    type: "success" | "error" | "info" = "info"
  ) {
    this.snackBar.open(message, "Close", {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
