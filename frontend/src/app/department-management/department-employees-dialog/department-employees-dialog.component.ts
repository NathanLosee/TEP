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
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Employee } from '../../../services/employee.service';
import {
  Department,
  DepartmentService,
} from '../../../services/department.service';

export interface DepartmentEmployeesDialogData {
  department: Department;
}

@Component({
  selector: 'app-department-employees-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatTooltipModule,
  ],
  templateUrl: './department-employees-dialog.component.html',
  styleUrl: './department-employees-dialog.component.scss',
})
export class DepartmentEmployeesDialogComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private departmentService = inject(DepartmentService);
  readonly data = inject<DepartmentEmployeesDialogData>(MAT_DIALOG_DATA);

  // Data
  employees: Employee[] = [];
  filteredEmployees: Employee[] = [];

  // Forms
  searchForm: FormGroup;

  // UI State
  isLoading = false;

  // Table columns
  displayedColumns: string[] = ['badge_number', 'first_name', 'last_name'];

  constructor() {
    this.searchForm = this.formBuilder.group({
      badge_number: [''],
      first_name: [''],
      last_name: [''],
    });
  }

  ngOnInit() {
    this.setupSearchForm();
    this.loadEmployees();
  }

  get department(): Department {
    return this.data.department;
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterEmployees();
    });
  }

  loadEmployees() {
    this.isLoading = true;
    this.departmentService.getEmployeesByDepartment(this.department.id!).subscribe({
      next: (employees) => {
        // Filter out root employee (id=0)
        this.employees = employees.filter(emp => emp.id !== 0);
        this.filterEmployees();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load employees:', error);
        this.isLoading = false;
      },
    });
  }

  filterEmployees() {
    const badgeNumberTerm =
      this.searchForm.get('badge_number')?.value?.toLowerCase().trim() || '';
    const firstNameTerm =
      this.searchForm.get('first_name')?.value?.toLowerCase().trim() || '';
    const lastNameTerm =
      this.searchForm.get('last_name')?.value?.toLowerCase().trim() || '';

    if (!badgeNumberTerm && !firstNameTerm && !lastNameTerm) {
      this.filteredEmployees = [...this.employees];
      return;
    }

    this.filteredEmployees = this.employees.filter((employee) => {
      const badgeNumberMatch = !badgeNumberTerm || 
        employee.badge_number.toLowerCase().includes(badgeNumberTerm);
      const firstNameMatch = !firstNameTerm || 
        employee.first_name.toLowerCase().includes(firstNameTerm);
      const lastNameMatch = !lastNameTerm || 
        employee.last_name.toLowerCase().includes(lastNameTerm);

      return badgeNumberMatch && firstNameMatch && lastNameMatch;
    });
  }

  clearSearch() {
    this.searchForm.reset();
  }
}