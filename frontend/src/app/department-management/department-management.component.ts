import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import {
  DepartmentService,
  Department,
} from '../../services/department.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { DepartmentFormDialogComponent } from './department-form-dialog/department-form-dialog.component';
import { DepartmentDetailsDialogComponent } from './department-details-dialog/department-details-dialog.component';

@Component({
  selector: 'app-department-management',
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
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatTabsModule,
  ],
  templateUrl: './department-management.component.html',
  styleUrl: './department-management.component.scss',
})
export class DepartmentManagementComponent implements OnInit {
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private departmentService = inject(DepartmentService);

  departments: Department[] = [];
  displayedColumns: string[] = ['name', 'actions'];

  isLoading = false;

  ngOnInit() {
    this.loadDepartments();
  }

  loadDepartments() {
    this.isLoading = true;
    this.departmentService.getDepartments().subscribe({
      next: (departments) => {
        this.departments = departments.map((dept) => ({
          ...dept,
        }));
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load departments', error);
        this.isLoading = false;
      },
    });
  }

  addDepartment() {
    const dialogRef = this.dialog.open(DepartmentFormDialogComponent, {
      width: '600px',
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.departments.push(result);
        this.showSnackBar(
          `Department "${result.name}" created successfully`,
          'success'
        );
      }
    });
  }

  // Action methods for buttons
  viewDepartment(department: Department) {
    const dialogRef = this.dialog.open(DepartmentDetailsDialogComponent, {
      width: '700px',
      data: { department },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'edit') {
        this.editDepartment(result.department);
      } else if (result?.action === 'delete') {
        this.deleteDepartment(result.department);
      }
    });
  }

  editDepartment(department: Department) {
    const dialogRef = this.dialog.open(DepartmentFormDialogComponent, {
      width: '600px',
      data: {
        editDepartment: department,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const index = this.departments.findIndex((dept) => dept.id === department.id);
        if (index > -1) {
          this.departments[index] = result;
          this.showSnackBar('Department updated successfully', 'success');
        }
      }
    });
  }

  private showSnackBar(
    message: string,
    type: 'success' | 'error' | 'info' = 'info'
  ) {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }

  deleteDepartment(department: Department) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${department.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      this.departmentService.deleteDepartment(department.id!).subscribe({
        next: () => {
          const index = this.departments.findIndex(
            (dept) => dept.id === department.id
          );
          if (index > -1) {
            this.departments.splice(index, 1);
            this.showSnackBar(
              `${department.name} has been deleted successfully`,
              'success'
            );
          }
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to delete department', error);
          this.isLoading = false;
        },
      });
    }
  }

  private handleError(message: string, error: any) {
    console.error(message, error);
    this.dialog.open(ErrorDialogComponent, {
      data: {
        title: 'Error',
        message: `${message}. Please try again.`,
        error: error?.error?.detail || error?.message || 'Unknown error',
      },
    });
  }
}
