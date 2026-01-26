import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import {
  TimeclockEntry,
  TimeclockEntryCreate,
  TimeclockService,
} from '../../../services/timeclock.service';
import { Employee, EmployeeService } from '../../../services/employee.service';
import { map, Observable, startWith } from 'rxjs';

export interface TimeclockEntryFormDialogData {
  editEntry?: {
    id: number;
    badge_number: string;
    employee_name?: string;
    clock_in: Date;
    clock_out?: Date;
  } | null;
  employees?: Employee[];
}

@Component({
  selector: 'app-timeclock-entry-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatSelectModule,
    MatAutocompleteModule,
  ],
  templateUrl: './timeclock-entry-form-dialog.component.html',
  styleUrl: './timeclock-entry-form-dialog.component.scss',
})
export class TimeclockEntryFormDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private timeclockService = inject(TimeclockService);
  private employeeService = inject(EmployeeService);
  private dialogRef = inject(MatDialogRef<TimeclockEntryFormDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as TimeclockEntryFormDialogData;

  entryForm!: FormGroup;
  isLoading = false;
  isEditMode = false;

  employees: Employee[] = [];
  filteredEmployees$!: Observable<Employee[]>;

  constructor() {
    this.isEditMode = !!this.data.editEntry;
  }

  ngOnInit() {
    this.initializeForm();
    this.loadEmployees();
  }

  private initializeForm() {
    const entry = this.data.editEntry;

    // For date/time fields, we need separate date and time inputs
    const clockInDate = entry?.clock_in ? new Date(entry.clock_in) : new Date();
    const clockOutDate = entry?.clock_out ? new Date(entry.clock_out) : null;

    this.entryForm = this.fb.group({
      badge_number: [entry?.badge_number || '', [Validators.required]],
      clock_in_date: [clockInDate, [Validators.required]],
      clock_in_time: [this.formatTime(clockInDate), [Validators.required]],
      clock_out_date: [clockOutDate],
      clock_out_time: [clockOutDate ? this.formatTime(clockOutDate) : ''],
    });

    // Setup autocomplete filtering
    this.filteredEmployees$ = this.entryForm.get('badge_number')!.valueChanges.pipe(
      startWith(''),
      map((value) => this.filterEmployees(value || ''))
    );
  }

  private formatTime(date: Date): string {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  private parseTime(timeStr: string): { hours: number; minutes: number } {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return { hours: hours || 0, minutes: minutes || 0 };
  }

  private filterEmployees(value: string): Employee[] {
    const filterValue = value.toLowerCase();
    return this.employees.filter(
      (employee) =>
        employee.badge_number.toLowerCase().includes(filterValue) ||
        `${employee.first_name} ${employee.last_name}`
          .toLowerCase()
          .includes(filterValue)
    );
  }

  private loadEmployees() {
    if (this.data.employees) {
      // Filter out root employee (id 0 or badge '000000')
      this.employees = this.data.employees.filter(
        (e) => e.id !== 0 && e.badge_number !== '000000'
      );
    } else {
      this.employeeService.getEmployees().subscribe({
        next: (employees) => {
          // Filter out root employee (id 0 or badge '000000')
          this.employees = employees.filter(
            (e) => e.id !== 0 && e.badge_number !== '000000'
          );
        },
        error: (error) => {
          console.error('Error loading employees:', error);
        },
      });
    }
  }

  displayEmployee(badge: string): string {
    if (!badge) return '';
    const employee = this.employees.find((e) => e.badge_number === badge);
    if (employee) {
      return `${employee.badge_number} - ${employee.first_name} ${employee.last_name}`;
    }
    return badge;
  }

  onEmployeeSelected(badge: string) {
    this.entryForm.patchValue({ badge_number: badge });
  }

  submitForm() {
    if (this.entryForm.valid) {
      this.isLoading = true;

      const formValue = this.entryForm.value;

      // Combine date and time for clock_in
      const clockInDate = new Date(formValue.clock_in_date);
      const clockInTime = this.parseTime(formValue.clock_in_time);
      clockInDate.setHours(clockInTime.hours, clockInTime.minutes, 0, 0);

      // Combine date and time for clock_out (if provided)
      let clockOutDate: Date | null = null;
      if (formValue.clock_out_date && formValue.clock_out_time) {
        clockOutDate = new Date(formValue.clock_out_date);
        const clockOutTime = this.parseTime(formValue.clock_out_time);
        clockOutDate.setHours(clockOutTime.hours, clockOutTime.minutes, 0, 0);
      }

      if (this.isEditMode && this.data.editEntry) {
        const updateData = {
          id: this.data.editEntry.id,
          badge_number: formValue.badge_number,
          clock_in: clockInDate.toISOString(),
          clock_out: clockOutDate ? clockOutDate.toISOString() : null,
        };

        this.timeclockService
          .updateTimeclockEntry(this.data.editEntry.id, updateData)
          .subscribe({
            next: (updatedEntry) => {
              this.dialogRef.close(updatedEntry);
              this.isLoading = false;
            },
            error: (error) => {
              console.error('Error updating entry:', error);
              this.isLoading = false;
            },
          });
      } else {
        const createData: TimeclockEntryCreate = {
          badge_number: formValue.badge_number,
          clock_in: clockInDate.toISOString(),
          clock_out: clockOutDate ? clockOutDate.toISOString() : null,
        };

        this.timeclockService.createTimeclockEntry(createData).subscribe({
          next: (newEntry) => {
            this.dialogRef.close(newEntry);
            this.isLoading = false;
          },
          error: (error) => {
            console.error('Error creating entry:', error);
            this.isLoading = false;
          },
        });
      }
    }
  }

  cancelForm() {
    this.dialogRef.close();
  }
}
