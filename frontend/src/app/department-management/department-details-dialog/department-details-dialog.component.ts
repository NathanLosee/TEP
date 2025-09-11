import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { Department } from '../../../services/department.service';
import { Employee } from '../../../services/employee.service';

export interface DepartmentDetailsDialogData {
  department: Department;
  employees?: Employee[];
}

@Component({
  selector: 'app-department-details-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
  ],
  templateUrl: './department-details-dialog.component.html',
  styleUrl: './department-details-dialog.component.scss',
})
export class DepartmentDetailsDialogComponent {
  private dialogRef = inject(MatDialogRef<DepartmentDetailsDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as DepartmentDetailsDialogData;

  get department() {
    return this.data.department;
  }

  get employees() {
    return this.data.employees || [];
  }

  closeDialog() {
    this.dialogRef.close();
  }

  editDepartment() {
    this.dialogRef.close({ action: 'edit', department: this.department });
  }

  manageEmployees() {
    this.dialogRef.close({ action: 'employees', department: this.department });
  }

  deleteDepartment() {
    this.dialogRef.close({ action: 'delete', department: this.department });
  }
}