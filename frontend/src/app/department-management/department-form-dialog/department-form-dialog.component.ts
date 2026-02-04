import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
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
import { Department, DepartmentService } from '../../../services/department.service';

export interface DepartmentFormDialogData {
  editDepartment?: Department | null;
}

@Component({
  selector: 'app-department-form-dialog',
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
    MatProgressSpinnerModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
  ],
  templateUrl: './department-form-dialog.component.html',
  styleUrl: './department-form-dialog.component.scss',
})
export class DepartmentFormDialogComponent {
  private fb = inject(FormBuilder);
  private departmentService = inject(DepartmentService);
  private dialogRef = inject(MatDialogRef<DepartmentFormDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as DepartmentFormDialogData;

  departmentForm!: FormGroup;
  isLoading = false;
  isEditMode = false;

  constructor() {
    this.isEditMode = !!this.data.editDepartment;
    this.initializeForm();
  }

  private initializeForm() {
    this.departmentForm = this.fb.group({
      name: [
        this.data.editDepartment?.name || '',
        [Validators.required],
      ],
    });
  }

  submitForm() {
    if (this.departmentForm.valid) {
      this.isLoading = true;

      const departmentData = this.departmentForm.value;

      if (this.isEditMode && this.data.editDepartment) {
        this.departmentService
          .updateDepartment(this.data.editDepartment.id!, departmentData)
          .subscribe({
            next: (updatedDepartment) => {
              this.dialogRef.close(updatedDepartment);
              this.isLoading = false;
            },
            error: (error) => {
              this.isLoading = false;
            },
          });
      } else {
        this.departmentService.createDepartment(departmentData).subscribe({
          next: (newDepartment) => {
            this.dialogRef.close(newDepartment);
            this.isLoading = false;
          },
          error: (error) => {
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