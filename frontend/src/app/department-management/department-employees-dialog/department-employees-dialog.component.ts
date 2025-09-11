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
  MatDialogTitle,
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
    MatDialogTitle,
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
  displayedColumns: string[] = ['badge_number', 'name', 'org_unit'];

  constructor() {
    this.searchForm = this.formBuilder.group({
      name: [''],
      badge_number: [''],
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
        this.employees = employees;
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
    const filters = this.searchForm.value;

    if (!filters.name && !filters.badge_number) {
      this.filteredEmployees = [...this.employees];
      return;
    }

    this.filteredEmployees = this.employees.filter((employee) => {
      const searchName = filters.name?.toLowerCase() || '';
      const searchBadge = filters.badge_number?.toLowerCase() || '';
      
      const matchesName = !searchName || 
        employee.first_name?.toLowerCase().includes(searchName) ||
        employee.last_name?.toLowerCase().includes(searchName);
      
      const matchesBadge = !searchBadge || 
        employee.badge_number?.toLowerCase().includes(searchBadge);

      return matchesName && matchesBadge;
    });
  }
}