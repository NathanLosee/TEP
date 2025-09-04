import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output, inject } from '@angular/core';
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
import { MatChipsModule } from '@angular/material/chips';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { HolidayGroup } from '../../../services/holiday-group.service';

@Component({
  selector: 'app-holiday-form',
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
  ],
  templateUrl: './holiday-form.component.html',
})
export class HolidayFormComponent {
  private formBuilder = inject(FormBuilder);

  holidayForm: FormGroup;
  isLoading = false;

  @Output() formSubmitted = new EventEmitter<HolidayGroup>();
  @Output() formCancelled = new EventEmitter<void>();

  constructor() {
    this.holidayForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      holidays: this.formBuilder.array([]),
    });
  }

  getHolidays(): FormArray {
    return this.holidayForm.get('holidays') as FormArray;
  }

  addHoliday() {
    this.getHolidays().push(
      this.formBuilder.group({
        name: ['', Validators.required],
        start_date: ['', Validators.required],
        end_date: ['', Validators.required],
      })
    );
  }

  removeHoliday(holidayIndex: number) {
    this.getHolidays().removeAt(holidayIndex);
  }

  getFormData(): HolidayGroup {
    const holidays = this.getHolidays().controls.map(
      (control) => control.value
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

  patchForm(group: HolidayGroup): void {
    this.holidayForm.patchValue({
      name: group.name,
    });
    this.getHolidays().clear();
    group.holidays.forEach((holiday) => {
      this.getHolidays().push(
        this.formBuilder.group({
          name: [holiday.name, Validators.required],
          start_date: [holiday.start_date, Validators.required],
          end_date: [holiday.end_date, Validators.required],
        })
      );
    });
  }

  submitForm() {
    if (this.holidayForm.valid) {
      this.formSubmitted.emit(this.getFormData());
    }
  }

  cancelForm() {
    this.formCancelled.emit();
    this.resetForm();
  }

  resetForm(): void {
    this.holidayForm.reset();
    this.getHolidays().clear();
  }
}
