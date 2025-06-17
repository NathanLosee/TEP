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
import { MatSelectModule } from "@angular/material/select";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatTabsModule } from "@angular/material/tabs";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { MatChipsModule } from "@angular/material/chips";

interface AnalyticsMetric {
  title: string;
  value: number;
  change: number;
  trend: "up" | "down" | "stable";
  format: "number" | "percentage" | "hours" | "currency";
}

interface DepartmentAnalytics {
  name: string;
  employees: number;
  avgHours: number;
  efficiency: number;
  overtime: number;
  attendance: number;
}

@Component({
  selector: "app-analytics",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatChipsModule,
  ],
  templateUrl: "./analytics.component.html",
  styleUrl: "./analytics.component.scss",
})
export class AnalyticsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);

  analyticsForm: FormGroup;
  isLoading = false;
  selectedTabIndex = 0;

  // Key Performance Indicators
  kpiMetrics: AnalyticsMetric[] = [
    {
      title: "Total Work Hours",
      value: 2456,
      change: 8.2,
      trend: "up",
      format: "hours",
    },
    {
      title: "Productivity Score",
      value: 87.5,
      change: 2.1,
      trend: "up",
      format: "percentage",
    },
    {
      title: "Overtime Hours",
      value: 142,
      change: -5.8,
      trend: "down",
      format: "hours",
    },
    {
      title: "Attendance Rate",
      value: 94.2,
      change: 1.3,
      trend: "up",
      format: "percentage",
    },
    {
      title: "Labor Cost",
      value: 52840,
      change: 3.7,
      trend: "up",
      format: "currency",
    },
    {
      title: "Efficiency Rating",
      value: 91.8,
      change: 0.5,
      trend: "stable",
      format: "percentage",
    },
    {
      title: "Holiday Utilization",
      value: 78.3,
      change: 4.2,
      trend: "up",
      format: "percentage",
    },
    {
      title: "Days Until Next Holiday",
      value: 12,
      change: -1,
      trend: "down",
      format: "number",
    },
  ];

  // Department Performance Data
  departmentData: DepartmentAnalytics[] = [
    {
      name: "IT",
      employees: 12,
      avgHours: 8.2,
      efficiency: 92.5,
      overtime: 15.2,
      attendance: 96.8,
    },
    {
      name: "Manufacturing",
      employees: 45,
      avgHours: 8.8,
      efficiency: 89.1,
      overtime: 28.5,
      attendance: 93.2,
    },
    {
      name: "Sales",
      employees: 18,
      avgHours: 7.9,
      efficiency: 88.7,
      overtime: 12.1,
      attendance: 95.1,
    },
    {
      name: "HR",
      employees: 6,
      avgHours: 8.0,
      efficiency: 94.2,
      overtime: 8.5,
      attendance: 97.5,
    },
  ];

  timePeriods = [
    { value: "today", label: "Today" },
    { value: "week", label: "This Week" },
    { value: "month", label: "This Month" },
    { value: "quarter", label: "This Quarter" },
    { value: "year", label: "This Year" },
    { value: "custom", label: "Custom Range" },
  ];

  constructor() {
    this.analyticsForm = this.fb.group({
      timePeriod: ["month"],
      department: [""],
      dateRange: this.fb.group({
        start: [this.getMonthStart()],
        end: [new Date()],
      }),
    });
  }

  ngOnInit() {
    this.setupFormWatchers();
  }

  setupFormWatchers() {
    this.analyticsForm.get("timePeriod")?.valueChanges.subscribe((period) => {
      this.updateDateRange(period);
    });
  }

  updateDateRange(period: string) {
    const today = new Date();
    let start: Date;

    switch (period) {
      case "today":
        start = new Date(today);
        break;
      case "week":
        start = new Date(today);
        start.setDate(today.getDate() - 7);
        break;
      case "month":
        start = this.getMonthStart();
        break;
      case "quarter":
        start = new Date(
          today.getFullYear(),
          Math.floor(today.getMonth() / 3) * 3,
          1,
        );
        break;
      case "year":
        start = new Date(today.getFullYear(), 0, 1);
        break;
      default:
        return; // Don't update for custom
    }

    this.analyticsForm.patchValue({
      dateRange: { start, end: today },
    });
  }

  refreshAnalytics() {
    this.isLoading = true;
    setTimeout(() => {
      this.isLoading = false;
      this.showSnackBar("Analytics refreshed successfully", "success");
    }, 2000);
  }

  exportAnalytics() {
    this.showSnackBar("Exporting analytics data...", "info");
    setTimeout(() => {
      this.showSnackBar("Analytics exported successfully", "success");
    }, 1500);
  }

  getMetricIcon(trend: string): string {
    switch (trend) {
      case "up":
        return "trending_up";
      case "down":
        return "trending_down";
      default:
        return "trending_flat";
    }
  }

  getMetricColor(trend: string): string {
    switch (trend) {
      case "up":
        return "success";
      case "down":
        return "error";
      default:
        return "neutral";
    }
  }

  formatMetricValue(value: number, format: string): string {
    switch (format) {
      case "percentage":
        return `${value}%`;
      case "hours":
        return `${value}h`;
      case "currency":
        return `$${value.toLocaleString()}`;
      default:
        return value.toLocaleString();
    }
  }

  getDepartmentEfficiencyClass(efficiency: number): string {
    if (efficiency >= 90) return "high-efficiency";
    if (efficiency >= 80) return "medium-efficiency";
    return "low-efficiency";
  }

  private getMonthStart(): Date {
    const today = new Date();
    return new Date(today.getFullYear(), today.getMonth(), 1);
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
