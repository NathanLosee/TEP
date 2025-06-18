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
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

interface Employee {
  id: number;
  badge_number: string;
  first_name: string;
  last_name: string;
  payroll_type: string;
  workweek_type: string;
  time_type: boolean;
  allow_clocking: boolean;
  allow_delete: boolean;
  org_unit?: any;
  manager?: any;
  departments?: any[];
  holiday_group?: any;
}

@Component({
  selector: 'app-employee-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatSlideToggleModule,
  ],
  templateUrl: './employee-management.component.html',
  styleUrl: './employee-management.component.scss',
})
export class EmployeeManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  employees: Employee[] = [];
  filteredEmployees: Employee[] = [];
  displayedColumns: string[] = [
    'badge_number',
    'name',
    'payroll_type',
    'org_unit',
    'departments',
    'holiday_group',
    'status',
    'actions',
  ];

  searchForm: FormGroup;
  isLoading = false;

  // Search filters
  searchFilters = {
    badge_number: '',
    first_name: '',
    last_name: '',
    department_name: '',
    org_unit_name: '',
  };

  constructor() {
    this.searchForm = this.fb.group({
      searchTerm: [''],
      department: [''],
      org_unit: [''],
      status: [''],
    });

    // Initialize empty edit form
    this.editForm = this.fb.group({
      badge_number: ['', [Validators.required]],
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      payroll_type: ['', [Validators.required]],
      workweek_type: ['', [Validators.required]],
      time_type: [false],
      allow_clocking: [true],
      allow_delete: [true],
    });
  }

  ngOnInit() {
    this.loadEmployees();
    this.setupSearchForm();
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterEmployees();
    });
  }

  loadEmployees() {
    this.isLoading = true;
    // Simulate API call - replace with actual service call
    setTimeout(() => {
      this.employees = this.generateMockEmployees();
      this.filteredEmployees = [...this.employees];
      this.isLoading = false;
    }, 1000);
  }

  filterEmployees() {
    const filters = this.searchForm.value;

    this.filteredEmployees = this.employees.filter((employee) => {
      const searchTerm = filters.searchTerm?.toLowerCase() || '';
      const matchesSearch =
        !searchTerm ||
        employee.badge_number.toLowerCase().includes(searchTerm) ||
        employee.first_name.toLowerCase().includes(searchTerm) ||
        employee.last_name.toLowerCase().includes(searchTerm);

      const matchesDepartment =
        !filters.department ||
        employee.departments?.some((dept) => dept.name === filters.department);

      const matchesOrgUnit =
        !filters.org_unit || employee.org_unit?.name === filters.org_unit;

      const matchesStatus =
        !filters.status ||
        (filters.status === 'active' && employee.allow_clocking) ||
        (filters.status === 'inactive' && !employee.allow_clocking);

      return (
        matchesSearch && matchesDepartment && matchesOrgUnit && matchesStatus
      );
    });
  }

  addEmployee() {
    // Open add employee dialog
    this.showSnackBar('Add employee feature coming soon', 'info');
  }

  selectedEmployee: Employee | null = null;
  showEditForm = false;
  showViewDetails = false;
  editForm: FormGroup;

  editEmployee(employee: Employee) {
    this.selectedEmployee = employee;
    this.showEditForm = true;
    this.showViewDetails = false;

    // Initialize edit form with employee data
    this.editForm = this.fb.group({
      badge_number: [employee.badge_number, [Validators.required]],
      first_name: [employee.first_name, [Validators.required]],
      last_name: [employee.last_name, [Validators.required]],
      payroll_type: [employee.payroll_type, [Validators.required]],
      workweek_type: [employee.workweek_type, [Validators.required]],
      time_type: [employee.time_type],
      allow_clocking: [employee.allow_clocking],
      allow_delete: [employee.allow_delete],
    });
  }

  viewEmployee(employee: Employee) {
    this.selectedEmployee = employee;
    this.showViewDetails = true;
    this.showEditForm = false;
  }

  deleteEmployee(employee: Employee) {
    if (!employee.allow_delete) {
      this.showSnackBar('This employee cannot be deleted', 'error');
      return;
    }

    const confirmDelete = confirm(
      `Are you sure you want to delete ${employee.first_name} ${employee.last_name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      // Remove employee from the array (simulating API call)
      setTimeout(() => {
        const index = this.employees.findIndex((emp) => emp.id === employee.id);
        if (index > -1) {
          this.employees.splice(index, 1);
          this.filterEmployees();
          this.showSnackBar(
            `${employee.first_name} ${employee.last_name} has been deleted successfully`,
            'success'
          );
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  saveEmployee() {
    if (this.editForm && this.editForm.valid && this.selectedEmployee) {
      this.isLoading = true;

      const formData = this.editForm.value;

      // Update employee data (simulating API call)
      setTimeout(() => {
        const index = this.employees.findIndex(
          (emp) => emp.id === this.selectedEmployee!.id
        );
        if (index > -1) {
          this.employees[index] = {
            ...this.employees[index],
            ...formData,
          };
          this.filterEmployees();
          this.showSnackBar('Employee updated successfully', 'success');
          this.cancelEdit();
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  cancelEdit() {
    this.showEditForm = false;
    this.showViewDetails = false;
    this.selectedEmployee = null;
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

  private generateMockEmployees(): Employee[] {
    return [
      {
        id: 1,
        badge_number: 'EMP001',
        first_name: 'John',
        last_name: 'Doe',
        payroll_type: 'Salary',
        workweek_type: 'Standard',
        time_type: true,
        allow_clocking: true,
        allow_delete: true,
        org_unit: { name: 'Corporate' },
        departments: [{ name: 'IT' }, { name: 'Admin' }],
        holiday_group: { name: 'Standard US Holidays' },
      },
      {
        id: 2,
        badge_number: 'EMP002',
        first_name: 'Jane',
        last_name: 'Smith',
        payroll_type: 'Hourly',
        workweek_type: 'Flexible',
        time_type: false,
        allow_clocking: true,
        allow_delete: true,
        org_unit: { name: 'Manufacturing' },
        departments: [{ name: 'Production' }],
        holiday_group: { name: 'Manufacturing Holidays' },
      },
      {
        id: 3,
        badge_number: 'EMP003',
        first_name: 'Mike',
        last_name: 'Johnson',
        payroll_type: 'Salary',
        workweek_type: 'Standard',
        time_type: true,
        allow_clocking: false,
        allow_delete: false,
        org_unit: { name: 'Corporate' },
        departments: [{ name: 'HR' }],
        holiday_group: { name: 'Corporate Holidays' },
      },
    ];
  }
}
