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
import {
  DepartmentService,
  Department,
} from '../../services/department.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

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
  ],
  templateUrl: './department-management.component.html',
  styleUrl: './department-management.component.scss',
})
export class DepartmentManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private departmentService = inject(DepartmentService);

  departments: Department[] = [];
  selectedDepartment?: Department;
  displayedColumns: string[] = ['name', 'actions'];

  addForm: FormGroup;
  editForm: FormGroup;

  isLoading = false;
  showAddForm = false;
  showEditForm = false;
  showEmployeeList = false;

  constructor() {
    this.addForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
    });

    this.editForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
    });
  }

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

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.addForm.reset();
    }
  }

  addDepartment() {
    if (this.addForm.valid) {
      this.isLoading = true;
      const departmentData = {
        name: this.addForm.get('name')?.value,
      };

      this.departmentService.createDepartment(departmentData).subscribe({
        next: (newDept) => {
          this.departments.push({ ...newDept });
          this.addForm.reset();
          this.showAddForm = false;
          this.showSnackBar(
            `Department "${newDept.name}" created successfully`,
            'success'
          );
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to create department', error);
          this.isLoading = false;
        },
      });
    }
  }

  // Action methods for buttons
  viewEmployees(department: Department) {
    this.isLoading = true;
    this.showEmployeeList = true;
    this.showEditForm = false;

    this.departmentService.getEmployeesByDepartment(department.id!).subscribe({
      next: (employees) => {
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load department employees', error);
        this.isLoading = false;
      },
    });
  }

  editDepartment(department: Department) {
    this.showEditForm = true;
    this.showEmployeeList = false;

    // Initialize edit form with department data
    this.editForm.patchValue({
      name: department.name,
    });
  }

  saveDepartment() {
    if (this.editForm && this.editForm.valid && this.selectedDepartment) {
      this.isLoading = true;

      const departmentData = {
        name: this.editForm.get('name')?.value,
      };

      this.departmentService
        .updateDepartment(this.selectedDepartment.id!, departmentData)
        .subscribe({
          next: (updatedDept) => {
            const index = this.departments.findIndex(
              (dept) => dept.id === this.selectedDepartment!.id
            );
            if (index > -1) {
              this.departments[index] = {
                ...this.departments[index],
                name: updatedDept.name,
              };
              this.showSnackBar('Department updated successfully', 'success');
              this.cancelEdit();
            }
            this.isLoading = false;
          },
          error: (error) => {
            this.handleError('Failed to update department', error);
            this.isLoading = false;
          },
        });
    }
  }

  cancelEdit() {
    this.showEditForm = false;
    this.showEmployeeList = false;
    this.selectedDepartment = undefined;
    this.editForm?.reset();
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
