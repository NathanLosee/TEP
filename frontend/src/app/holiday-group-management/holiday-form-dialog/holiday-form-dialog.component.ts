import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  FormArray,
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { HolidayGroup } from '../../../services/holiday-group.service';

export interface HolidayFormDialogData {
  editGroup?: HolidayGroup | null;
}

@Component({
  selector: 'app-holiday-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatTabsModule,
    MatCheckboxModule,
    MatSelectModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
  ],
  templateUrl: './holiday-form-dialog.component.html',
  styleUrl: './holiday-form-dialog.component.scss',
})
export class HolidayFormDialogComponent {
  private formBuilder = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<HolidayFormDialogComponent>);
  readonly data = inject<HolidayFormDialogData>(MAT_DIALOG_DATA);

  holidayForm: FormGroup;
  isEditMode = false;
  isLoading = false;

  // Constants for recurring holiday options
  readonly weekdayNames = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
  ];
  readonly weekNumbers = [
    { value: 1, label: 'First' },
    { value: 2, label: 'Second' },
    { value: 3, label: 'Third' },
    { value: 4, label: 'Fourth' },
    { value: 5, label: 'Last' },
  ];
  readonly monthNames = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];

  constructor() {
    this.holidayForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      holidays: this.formBuilder.array([]),
    });

    if (this.data.editGroup) {
      this.isEditMode = true;
      this.holidayForm = this.formBuilder.group({
        name: [this.data.editGroup.name, [Validators.required]],
        holidays: this.formBuilder.array([]),
      });
      this.data.editGroup.holidays.forEach((holiday) => {
        this.getHolidays().push(this.createHolidayFormGroup(holiday));
      });
    }
  }

  private createHolidayFormGroup(holiday?: any): FormGroup {
    return this.formBuilder.group({
      name: [holiday?.name || '', Validators.required],
      start_date: [
        holiday?.start_date ? new Date(holiday.start_date) : '',
        Validators.required,
      ],
      end_date: [
        holiday?.end_date ? new Date(holiday.end_date) : '',
        Validators.required,
      ],
      is_recurring: [holiday?.is_recurring || false],
      recurrence_type: [holiday?.recurrence_type || null],
      recurrence_month: [holiday?.recurrence_month || null],
      recurrence_day: [holiday?.recurrence_day || null],
      recurrence_week: [holiday?.recurrence_week || null],
      recurrence_weekday: [holiday?.recurrence_weekday || null],
    });
  }

  getHolidays(): FormArray {
    return this.holidayForm.get('holidays') as FormArray;
  }

  addHoliday() {
    this.getHolidays().push(this.createHolidayFormGroup());
  }

  removeHoliday(holidayIndex: number) {
    this.getHolidays().removeAt(holidayIndex);
  }

  getFormData(): HolidayGroup {
    const holidays = this.getHolidays().controls.map(
      (control) => control.value,
    );
    holidays.forEach((holiday: any) => {
      // Convert to Date only strings
      holiday.start_date = new Date(holiday.start_date)
        .toISOString()
        .split('T')[0];
      holiday.end_date = new Date(holiday.end_date).toISOString().split('T')[0];
    });
    return {
      name: this.holidayForm.get('name')?.value,
      holidays: holidays,
    };
  }

  submitForm() {
    if (this.holidayForm.valid) {
      const formData = this.getFormData();
      if (this.data.editGroup) {
        formData.id = this.data.editGroup.id;
      }
      this.dialogRef.close(formData);
    }
  }

  cancelForm() {
    this.dialogRef.close();
  }
}
