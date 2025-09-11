import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PartialObserver } from 'rxjs';
import {
  Department,
  DepartmentService,
} from '../../services/department.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { DepartmentEmployeesDialogComponent } from './department-employees-dialog/department-employees-dialog.component';
import { DepartmentFormDialogComponent } from './department-form-dialog/department-form-dialog.component';

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
  private formBuilder = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);

  private departmentService = inject(DepartmentService);

  // Data
  departments: Department[] = [];
  filteredDepartments: Department[] = [];
  selectedDepartment: Department | null = null;

  // Forms
  searchForm: FormGroup;

  // UI State
  isLoading = false;

  // Table columns
  displayedColumns: string[] = ['name', 'actions'];

  constructor() {
    this.searchForm = this.formBuilder.group({
      name: [''],
    });
  }

  ngOnInit() {
    this.setupSearchForm();
    this.loadDepartments();
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterDepartments();
    });
  }

  loadDepartments() {
    this.isLoading = true;
    this.departmentService.getDepartments().subscribe({
      next: (departments) => {
        this.departments = departments.map((dept) => ({
          ...dept,
          employee_count: 0, // Will be loaded separately if needed
        }));
        this.filterDepartments();
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load departments', error);
        this.isLoading = false;
      },
    });
  }

  filterDepartments() {
    const filters = this.searchForm.value;

    if (!filters.name) {
      this.filteredDepartments = [...this.departments];
      return;
    }
    this.filteredDepartments = this.departments.filter((department) => {
      const searchName = filters.name?.toLowerCase() || '';
      const matchesSearch =
        !searchName || department.name.toLowerCase().includes(searchName);

      return matchesSearch;
    });
  }

  viewEmployees(department: Department) {
    this.dialog.open(DepartmentEmployeesDialogComponent, {
      width: '800px',
      maxWidth: '90vw',
      data: { department },
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });
  }

  openDepartmentFormDialog(editDepartment?: Department) {
    const dialogRef = this.dialog.open(DepartmentFormDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: { editDepartment },
      disableClose: true,
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });

    dialogRef.afterClosed().subscribe((result: Department | undefined) => {
      if (result) {
        this.saveDepartment(result);
      }
    });
  }

  saveDepartment(departmentData: Department) {
    this.isLoading = true;
    if (this.selectedDepartment) {
      departmentData.id = this.selectedDepartment.id;
    }

    const observer: PartialObserver<Department> = {
      next: (returnedDepartment) => {
        if (this.selectedDepartment) {
          // Replace existing department
          const index = this.departments.findIndex(
            (d) => d.id === this.selectedDepartment!.id
          );
          if (index > -1) {
            this.departments[index] = returnedDepartment;
          }
        } else {
          // Add new department
          this.departments.push(returnedDepartment);
        }
        this.filterDepartments();
        this.showSnackBar('Department updated successfully', 'success');
        this.selectedDepartment = null;
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to update department', error);
        this.isLoading = false;
      },
    };

    if (this.selectedDepartment) {
      // Editing an existing department
      this.departmentService
        .updateDepartment(this.selectedDepartment.id!, departmentData)
        .subscribe(observer);
    } else {
      // Creating a new department
      this.departmentService
        .createDepartment(departmentData)
        .subscribe(observer);
    }
  }

  deleteDepartment(department: Department) {
    if (
      confirm(
        `Are you sure you want to delete "${department.name}"? This action cannot be undone.`
      )
    ) {
      this.isLoading = true;
      this.departmentService.deleteDepartment(department.id!).subscribe({
        next: () => {
          const index = this.departments.findIndex(
            (d) => d.id === department.id
          );
          if (index > -1) {
            this.departments.splice(index, 1);
            this.filterDepartments();
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

  private showSnackBar(
    message: string,
    type: 'success' | 'error' | 'info' = 'info'
  ) {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
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
