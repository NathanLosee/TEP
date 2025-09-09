import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  inject,
} from '@angular/core';
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
export class HolidayFormComponent implements OnInit {
  @Input() editGroup: HolidayGroup | null = null;

  private formBuilder = inject(FormBuilder);

  holidayForm: FormGroup;
  isEditMode = false;
  isLoading = false;

  @Output() formSubmitted = new EventEmitter<HolidayGroup>();
  @Output() formCancelled = new EventEmitter<void>();

  constructor() {
    this.holidayForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      holidays: this.formBuilder.array([]),
    });
  }

  ngOnInit() {
    if (this.editGroup) {
      this.isEditMode = true;
      this.holidayForm = this.formBuilder.group({
        name: [this.editGroup.name, [Validators.required]],
        holidays: this.formBuilder.array([]),
      });
      this.editGroup.holidays.forEach((holiday) => {
        this.getHolidays().push(
          this.formBuilder.group({
            name: [holiday.name, Validators.required],
            start_date: [new Date(holiday.start_date), Validators.required],
            end_date: [new Date(holiday.end_date), Validators.required],
          })
        );
      });
    }
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

  submitForm() {
    this.isEditMode = false;
    if (this.holidayForm.valid) {
      this.formSubmitted.emit(this.getFormData());
    }
  }

  cancelForm() {
    this.isEditMode = false;
    this.formCancelled.emit();
    this.resetForm();
  }

  resetForm(): void {
    this.holidayForm.reset();
    this.getHolidays().clear();
  }
}
