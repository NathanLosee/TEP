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
import { DepartmentService, Department, DepartmentWithEmployees } from '../../services/department.service';
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
  filteredDepartments: Department[] = [];
  selectedDepartmentDetails: DepartmentWithEmployees | null = null;
  displayedColumns: string[] = ['name', 'employee_count', 'actions'];

  searchForm: FormGroup;
  addDepartmentForm: FormGroup;
  editForm: FormGroup;

  isLoading = false;
  showAddForm = false;
  showEditForm = false;
  showEmployeeList = false;
  selectedDepartment: Department | null = null;

  constructor() {
    this.searchForm = this.fb.group({
      searchTerm: [''],
    });

    this.addDepartmentForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
    });

    this.editForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
    });
  }

  ngOnInit() {
    this.loadDepartments();
    this.setupSearchForm();
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
        this.departments = departments.map(dept => ({
          ...dept,
          employee_count: 0 // Will be populated when viewing details
        }));
        this.filteredDepartments = [...this.departments];
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load departments', error);
        this.isLoading = false;
      }
    });
  }

  filterDepartments() {
    const searchTerm =
      this.searchForm.get('searchTerm')?.value?.toLowerCase() || '';

    this.filteredDepartments = this.departments.filter((dept) =>
      dept.name.toLowerCase().includes(searchTerm)
    );
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.addDepartmentForm.reset();
    }
  }

  addDepartment() {
    if (this.addDepartmentForm.valid) {
      this.isLoading = true;
      const departmentData = {
        name: this.addDepartmentForm.get('name')?.value
      };

      this.departmentService.createDepartment(departmentData).subscribe({
        next: (newDept) => {
          this.departments.push({ ...newDept, employee_count: 0 });
          this.filterDepartments();
          this.addDepartmentForm.reset();
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
        }
      });
    }
  }

  // Action methods for buttons
  viewEmployees(department: Department) {
    this.selectedDepartment = department;
    this.isLoading = true;
    this.showEmployeeList = true;
    this.showEditForm = false;

    this.departmentService.getDepartmentById(department.id).subscribe({
      next: (departmentDetails) => {
        this.selectedDepartmentDetails = departmentDetails;
        // Update employee count in the main list
        const index = this.departments.findIndex(d => d.id === department.id);
        if (index > -1) {
          this.departments[index].employee_count = departmentDetails.employees.length;
          this.filterDepartments();
        }
        this.isLoading = false;
        this.showSnackBar(`Viewing employees for ${department.name}`, 'info');
      },
      error: (error) => {
        this.handleError('Failed to load department details', error);
        this.isLoading = false;
      }
    });
  }

  editDepartment(department: Department) {
    this.selectedDepartment = department;
    this.showEditForm = true;
    this.showEmployeeList = false;

    // Initialize edit form with department data
    this.editForm.patchValue({
      name: department.name,
    });
  }

  deleteDepartment(department: Department) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${department.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      this.departmentService.deleteDepartment(department.id).subscribe({
        next: () => {
          const index = this.departments.findIndex(
            (dept) => dept.id === department.id
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
        }
      });
    }
  }

  saveDepartment() {
    if (this.editForm && this.editForm.valid && this.selectedDepartment) {
      this.isLoading = true;

      const formData = this.editForm.value;

      // Update department data (simulating API call)
      setTimeout(() => {
        const index = this.departments.findIndex(
          (dept) => dept.id === this.selectedDepartment!.id
        );
        if (index > -1) {
          this.departments[index] = {
            ...this.departments[index],
            name: formData.name,
          };
          this.filterDepartments();
          this.showSnackBar('Department updated successfully', 'success');
          this.cancelEdit();
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  cancelEdit() {
    this.showEditForm = false;
    this.showEmployeeList = false;
    this.selectedDepartment = null;
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

  private generateMockDepartments(): Department[] {
    return [
      {
        id: 1,
        name: 'Information Technology',
        employee_count: 12,
      },
      {
        id: 2,
        name: 'Human Resources',
        employee_count: 5,
      },
      {
        id: 3,
        name: 'Production',
        employee_count: 25,
      },
      {
        id: 4,
        name: 'Quality Assurance',
        employee_count: 8,
      },
      {
        id: 5,
        name: 'Administration',
        employee_count: 6,
      },
      {
        id: 6,
        name: 'Sales & Marketing',
        employee_count: 15,
      },
    ];
  }
}
