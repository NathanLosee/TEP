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
import { Employee } from '../../../services/employee.service';

export interface EmployeeDetailsDialogData {
  employee: Employee;
}

@Component({
  selector: 'app-employee-details-dialog',
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
  templateUrl: './employee-details-dialog.component.html',
  styleUrl: './employee-details-dialog.component.scss',
})
export class EmployeeDetailsDialogComponent {
  private dialogRef = inject(MatDialogRef<EmployeeDetailsDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as EmployeeDetailsDialogData;

  get employee() {
    return this.data.employee;
  }

  closeDialog() {
    this.dialogRef.close();
  }

  editEmployee() {
    this.dialogRef.close({ action: 'edit', employee: this.employee });
  }

  deleteEmployee() {
    this.dialogRef.close({ action: 'delete', employee: this.employee });
  }
}