import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
} from "@angular/forms";
import { MatTableModule } from "@angular/material/table";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatSortModule } from "@angular/material/sort";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatSelectModule } from "@angular/material/select";
import { MatDialogModule } from "@angular/material/dialog";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatChipsModule } from "@angular/material/chips";

interface TimeclockEntry {
  id: number;
  badge_number: string;
  employee_name?: string;
  clock_in: Date;
  clock_out?: Date;
  total_hours?: number;
  status: "clocked_in" | "clocked_out" | "incomplete";
}

@Component({
  selector: "app-time-entries",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSelectModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatChipsModule,
  ],
  templateUrl: "./time-entries.component.html",
  styleUrl: "./time-entries.component.scss",
})
export class TimeEntriesComponent implements OnInit {
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);

  timeEntries: TimeclockEntry[] = [];
  filteredEntries: TimeclockEntry[] = [];
  displayedColumns: string[] = [
    "badge_number",
    "employee_name",
    "clock_in",
    "clock_out",
    "total_hours",
    "status",
    "actions",
  ];

  filterForm: FormGroup;
  isLoading = false;

  constructor() {
    this.filterForm = this.fb.group({
      dateRange: this.fb.group({
        start: [new Date()],
        end: [new Date()],
      }),
      badge_number: [""],
      status: [""],
    });
  }

  ngOnInit() {
    this.setDefaultDateRange();
    this.loadTimeEntries();
    this.setupFilterForm();
  }

  setDefaultDateRange() {
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());

    this.filterForm.patchValue({
      dateRange: {
        start: startOfWeek,
        end: today,
      },
    });
  }

  setupFilterForm() {
    this.filterForm.valueChanges.subscribe(() => {
      this.filterEntries();
    });
  }

  loadTimeEntries() {
    this.isLoading = true;
    // Simulate API call - replace with actual service call
    setTimeout(() => {
      this.timeEntries = this.generateMockTimeEntries();
      this.filteredEntries = [...this.timeEntries];
      this.isLoading = false;
    }, 1000);
  }

  filterEntries() {
    const filters = this.filterForm.value;
    const startDate = filters.dateRange?.start;
    const endDate = filters.dateRange?.end;

    this.filteredEntries = this.timeEntries.filter((entry) => {
      const entryDate = new Date(entry.clock_in);

      const matchesDateRange =
        (!startDate || entryDate >= startDate) &&
        (!endDate || entryDate <= endDate);

      const matchesBadge =
        !filters.badge_number ||
        entry.badge_number
          .toLowerCase()
          .includes(filters.badge_number.toLowerCase());

      const matchesStatus = !filters.status || entry.status === filters.status;

      return matchesDateRange && matchesBadge && matchesStatus;
    });
  }

  editEntry(entry: TimeclockEntry) {
    this.showSnackBar(`Edit entry for ${entry.badge_number}`, "info");
  }

  deleteEntry(entry: TimeclockEntry) {
    this.showSnackBar(`Delete entry for ${entry.badge_number}`, "info");
  }

  exportEntries() {
    this.showSnackBar("Export functionality coming soon", "info");
  }

  addManualEntry() {
    this.showSnackBar("Add manual entry feature coming soon", "info");
  }

  calculateTotalHours(clockIn: Date, clockOut?: Date): number {
    if (!clockOut) return 0;
    return (
      Math.round(
        ((clockOut.getTime() - clockIn.getTime()) / (1000 * 60 * 60)) * 100,
      ) / 100
    );
  }

  getStatusClass(status: string): string {
    switch (status) {
      case "clocked_in":
        return "status-active";
      case "clocked_out":
        return "status-complete";
      case "incomplete":
        return "status-warning";
      default:
        return "";
    }
  }

  getActiveEntriesCount(): number {
    return this.filteredEntries.filter((e) => e.status === "clocked_in").length;
  }

  getCompletedEntriesCount(): number {
    return this.filteredEntries.filter((e) => e.status === "clocked_out")
      .length;
  }

  getIncompleteEntriesCount(): number {
    return this.filteredEntries.filter((e) => e.status === "incomplete").length;
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

  private generateMockTimeEntries(): TimeclockEntry[] {
    const entries: TimeclockEntry[] = [];
    const today = new Date();

    for (let i = 0; i < 20; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - Math.floor(Math.random() * 7));

      const clockIn = new Date(date);
      clockIn.setHours(
        8 + Math.floor(Math.random() * 2),
        Math.floor(Math.random() * 60),
      );

      const clockOut = Math.random() > 0.2 ? new Date(clockIn) : undefined;
      if (clockOut) {
        clockOut.setHours(
          clockIn.getHours() + 8 + Math.floor(Math.random() * 2),
          Math.floor(Math.random() * 60),
        );
      }

      const badgeNumber = `EMP${String(i + 1).padStart(3, "0")}`;
      const status = !clockOut
        ? "clocked_in"
        : clockOut.getTime() - clockIn.getTime() < 4 * 60 * 60 * 1000
          ? "incomplete"
          : "clocked_out";

      entries.push({
        id: i + 1,
        badge_number: badgeNumber,
        employee_name: this.getRandomEmployeeName(),
        clock_in: clockIn,
        clock_out: clockOut,
        total_hours: clockOut ? this.calculateTotalHours(clockIn, clockOut) : 0,
        status: status as any,
      });
    }

    return entries.sort((a, b) => b.clock_in.getTime() - a.clock_in.getTime());
  }

  private getRandomEmployeeName(): string {
    const names = [
      "John Doe",
      "Jane Smith",
      "Mike Johnson",
      "Sarah Williams",
      "David Brown",
      "Lisa Davis",
      "Robert Miller",
      "Maria Garcia",
      "James Wilson",
      "Jennifer Moore",
    ];
    return names[Math.floor(Math.random() * names.length)];
  }
}
