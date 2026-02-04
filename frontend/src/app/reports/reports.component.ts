import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  Department,
  DepartmentService,
} from '../../services/department.service';
import { Employee, EmployeeService } from '../../services/employee.service';
import { OrgUnit, OrgUnitService } from '../../services/org-unit.service';
import {
  DayDetail,
  EmployeeReportData,
  ReportResponse,
  ReportService,
} from '../../services/report.service';

interface CalendarDay {
  date: Date;
  dateString: string; // YYYY-MM-DD format
  isCurrentMonth: boolean;
  isToday: boolean;
  dayDetail?: DayDetail;
}

interface EmployeeCalendar {
  currentMonth: Date;
  calendarDays: CalendarDay[];
  canGoPrevious: boolean;
  canGoNext: boolean;
  earliestDate?: Date;
  latestDate?: Date;
}

@Component({
  selector: 'app-reports',
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
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss',
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

  employees: Employee[] = [];
  departments: Department[] = [];
  orgUnits: OrgUnit[] = [];

  reportTypes = [
    { value: 'all', label: 'All Employees' },
    { value: 'employee', label: 'Individual Employee' },
    { value: 'department', label: 'Department' },
    { value: 'org_unit', label: 'Organizational Unit' },
  ];

  allDetailLevels = [
    { value: 'summary', label: 'Summary Only' },
    { value: 'employee_summary', label: 'Summary + Employee Details' },
    { value: 'detailed', label: 'Full Detailed Report' },
  ];

  // Filtered detail levels (excludes "summary" for single employee reports)
  get detailLevels() {
    const reportType = this.reportForm?.get('reportType')?.value;
    if (reportType === 'employee') {
      // For individual employee, summary only produces empty content
      return this.allDetailLevels.filter((level) => level.value !== 'summary');
    }
    return this.allDetailLevels;
  }

  // Track expansion state for employees (show/hide calendar)
  expandedEmployees: Set<number> = new Set();

  // Calendar state for each employee
  employeeCalendars: Map<number, EmployeeCalendar> = new Map();

  userTimezone: string;

  constructor() {
    this.userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    this.reportForm = this.fb.group({
      reportType: ['all'],
      dateRange: this.fb.group({
        start: [this.getLastWeekStart(), Validators.required],
        end: [new Date(), Validators.required],
      }),
      employee: [null],
      department: [null],
      orgUnit: [null],
      detailLevel: ['summary'],
    });

    // Subscribe to report type changes to reset filters
    this.reportForm.get('reportType')?.valueChanges.subscribe((reportType) => {
      this.reportForm.patchValue({
        employee: null,
        department: null,
        orgUnit: null,
      });
      // For individual employee reports, "summary" is not valid - reset to "employee_summary"
      if (
        reportType === 'employee' &&
        this.reportForm.get('detailLevel')?.value === 'summary'
      ) {
        this.reportForm.patchValue({ detailLevel: 'employee_summary' });
      }
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
        // Filter out root employee (id=0)
        this.employees = data.filter((emp) => emp.id !== 0);
      },
      error: (error) => {
        console.error('Error loading employees:', error);
        this.showSnackBar('Failed to load employees', 'error');
      },
    });
  }

  loadDepartments() {
    this.departmentService.getDepartments().subscribe({
      next: (data) => {
        this.departments = data;
      },
      error: (error) => {
        console.error('Error loading departments:', error);
        this.showSnackBar('Failed to load departments', 'error');
      },
    });
  }

  loadOrgUnits() {
    this.orgUnitService.getOrgUnits().subscribe({
      next: (data) => {
        // Filter out root org unit (id=0)
        this.orgUnits = data.filter((unit) => unit.id !== 0);
      },
      error: (error) => {
        console.error('Error loading org units:', error);
        this.showSnackBar('Failed to load org units', 'error');
      },
    });
  }

  generateReport() {
    if (this.reportForm.invalid) {
      this.showSnackBar('Please fill in all required fields', 'error');
      return;
    }

    this.isLoading = true;
    const formValue = this.reportForm.value;
    const reportType = formValue.reportType;

    const request = {
      start_date: this.formatDate(formValue.dateRange.start),
      end_date: this.formatDate(formValue.dateRange.end),
      employee_id: reportType === 'employee' ? formValue.employee : undefined,
      department_id:
        reportType === 'department' ? formValue.department : undefined,
      org_unit_id: reportType === 'org_unit' ? formValue.orgUnit : undefined,
    };

    this.reportService.generateReport(request).subscribe({
      next: (data) => {
        this.reportData = data;
        this.isLoading = false;
        this.expandedEmployees.clear();
        this.employeeCalendars.clear();

        // Initialize calendars for each employee
        data.employees.forEach((employee) => {
          this.initializeEmployeeCalendar(employee);
        });

        this.showSnackBar('Report generated successfully', 'success');
      },
      error: (error) => {
        console.error('Error generating report:', error);
        this.isLoading = false;
        this.showSnackBar('Failed to generate report', 'error');
      },
    });
  }

  exportPDF() {
    if (!this.reportData) {
      this.showSnackBar('Please generate a report first', 'error');
      return;
    }

    const formValue = this.reportForm.value;
    const reportType = formValue.reportType;

    this.reportService
      .exportPDF(
        this.formatDate(formValue.dateRange.start),
        this.formatDate(formValue.dateRange.end),
        formValue.detailLevel,
        reportType === 'employee' ? formValue.employee : undefined,
        reportType === 'department' ? formValue.department : undefined,
        reportType === 'org_unit' ? formValue.orgUnit : undefined,
      )
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `timeclock_report_${this.formatDate(formValue.dateRange.start)}_to_${this.formatDate(formValue.dateRange.end)}.pdf`;
          link.click();
          window.URL.revokeObjectURL(url);
          this.showSnackBar('PDF exported successfully', 'success');
        },
        error: (error) => {
          console.error('Error exporting PDF:', error);
          this.showSnackBar('Failed to export PDF', 'error');
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

  getEmployeeCalendar(employeeId: number): EmployeeCalendar | undefined {
    return this.employeeCalendars.get(employeeId);
  }

  initializeEmployeeCalendar(employee: EmployeeReportData) {
    if (!this.reportData) return;

    // Find earliest and latest dates in employee's data
    let earliestDate: Date | undefined;
    let latestDate: Date | undefined;

    employee.months.forEach((month) => {
      month.days.forEach((day) => {
        const dayDate = new Date(day.date);
        if (!earliestDate || dayDate < earliestDate) {
          earliestDate = dayDate;
        }
        if (!latestDate || dayDate > latestDate) {
          latestDate = dayDate;
        }
      });
    });

    // Start with the earliest month or report start date
    const startMonth = earliestDate || new Date(this.reportData.start_date);

    const calendar: EmployeeCalendar = {
      currentMonth: new Date(
        startMonth.getFullYear(),
        startMonth.getMonth(),
        1,
      ),
      calendarDays: [],
      canGoPrevious: true,
      canGoNext: true,
      earliestDate: earliestDate,
      latestDate: latestDate,
    };

    this.updateEmployeeCalendar(employee.employee_id, calendar, employee);
    this.employeeCalendars.set(employee.employee_id, calendar);
  }

  updateEmployeeCalendar(
    employeeId: number,
    calendar: EmployeeCalendar,
    employee: EmployeeReportData,
  ) {
    const year = calendar.currentMonth.getFullYear();
    const month = calendar.currentMonth.getMonth();

    // Get first day of the month
    const firstDay = new Date(year, month, 1);
    const firstDayOfWeek = firstDay.getDay();

    // Start from the Sunday before the first day of the month
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDayOfWeek);

    // Build calendar days array (6 weeks = 42 days)
    const calendarDays: CalendarDay[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Create a map of date strings to day details for quick lookup
    const dayDetailsMap = new Map<string, DayDetail>();
    employee.months.forEach((m) => {
      m.days.forEach((day) => {
        const dateStr = this.formatDate(new Date(day.date));
        dayDetailsMap.set(dateStr, day);
      });
    });

    for (let i = 0; i < 42; i++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + i);
      currentDate.setHours(0, 0, 0, 0);

      const dateStr = this.formatDate(currentDate);
      const dayDetail = dayDetailsMap.get(dateStr);

      calendarDays.push({
        date: new Date(currentDate),
        dateString: dateStr,
        isCurrentMonth: currentDate.getMonth() === month,
        isToday: currentDate.getTime() === today.getTime(),
        dayDetail: dayDetail,
      });
    }

    calendar.calendarDays = calendarDays;

    // Update navigation availability
    if (calendar.earliestDate) {
      const earliestMonth = new Date(
        calendar.earliestDate.getFullYear(),
        calendar.earliestDate.getMonth(),
        1,
      );
      calendar.canGoPrevious = calendar.currentMonth > earliestMonth;
    }

    if (calendar.latestDate) {
      const latestMonth = new Date(
        calendar.latestDate.getFullYear(),
        calendar.latestDate.getMonth(),
        1,
      );
      calendar.canGoNext = calendar.currentMonth < latestMonth;
    }
  }

  previousMonth(employeeId: number) {
    const calendar = this.employeeCalendars.get(employeeId);
    const employee = this.reportData?.employees.find(
      (e) => e.employee_id === employeeId,
    );

    if (calendar && employee && calendar.canGoPrevious) {
      const newMonth = new Date(calendar.currentMonth);
      newMonth.setMonth(newMonth.getMonth() - 1);
      calendar.currentMonth = newMonth;
      this.updateEmployeeCalendar(employeeId, calendar, employee);
    }
  }

  nextMonth(employeeId: number) {
    const calendar = this.employeeCalendars.get(employeeId);
    const employee = this.reportData?.employees.find(
      (e) => e.employee_id === employeeId,
    );

    if (calendar && employee && calendar.canGoNext) {
      const newMonth = new Date(calendar.currentMonth);
      newMonth.setMonth(newMonth.getMonth() + 1);
      calendar.currentMonth = newMonth;
      this.updateEmployeeCalendar(employeeId, calendar, employee);
    }
  }

  getTotalHours(): number {
    if (!this.reportData) return 0;
    return this.reportData.employees.reduce(
      (sum, emp) => sum + emp.summary.total_hours,
      0,
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
      0,
    );
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private getLastWeekStart(): Date {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date;
  }

  private showSnackBar(
    message: string,
    type: 'success' | 'error' | 'info' = 'info',
  ) {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
