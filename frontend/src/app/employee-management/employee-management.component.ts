import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableDataSource } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Department, DepartmentService } from '../../services/department.service';
import { Employee, EmployeeService } from '../../services/employee.service';
import { HolidayGroup, HolidayGroupService } from '../../services/holiday-group.service';
import { OrgUnit, OrgUnitService } from '../../services/org-unit.service';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';
import { ErrorDialogComponent, extractErrorDetail } from '../error-dialog/error-dialog.component';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../shared/models/table.models';
import { EmployeeDetailsDialogComponent } from './employee-details-dialog/employee-details-dialog.component';
import { EmployeeFormDialogComponent } from './employee-form-dialog/employee-form-dialog.component';

interface EmployeeListing {
  id: number;
  badge_number: string;
  name: string;
  payroll_type: string;
  org_unit: string;
  departments: string;
  holiday_group: string;
  status: string;
  // Keep reference to original employee for actions
  _employee: Employee;
}

@Component({
  selector: 'app-employee-management',
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
    MatSelectModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatTabsModule,
    DisableIfNoPermissionDirective,
    GenericTableComponent,
    TableCellDirective,
  ],
  templateUrl: './employee-management.component.html',
  styleUrl: './employee-management.component.scss',
})
export class EmployeeManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private employeeService = inject(EmployeeService);
  private departmentService = inject(DepartmentService);
  private orgUnitService = inject(OrgUnitService);
  private holidayGroupService = inject(HolidayGroupService);

  dataSource = new MatTableDataSource<EmployeeListing>([]);
  departments: Department[] = [];
  orgUnits: OrgUnit[] = [];
  holidayGroups: HolidayGroup[] = [];
  managers: Employee[] = [];

  // Table configuration
  columns: TableColumn<EmployeeListing>[] = [
    {
      key: 'badge_number',
      header: 'Badge #',
      type: 'template',
      sortable: true,
    },
    {
      key: 'name',
      header: 'Name',
      type: 'template',
      sortable: true,
    },
    {
      key: 'payroll_type',
      header: 'Payroll',
      type: 'template',
      sortable: true,
    },
    {
      key: 'org_unit',
      header: 'Org Unit',
      type: 'icon-text',
      icon: 'business',
      sortable: true,
    },
    {
      key: 'departments',
      header: 'Departments',
      type: 'text',
      sortable: true,
    },
    {
      key: 'holiday_group',
      header: 'Holiday Group',
      type: 'icon-text',
      icon: 'event',
      sortable: true,
    },
    {
      key: 'status',
      header: 'Status',
      type: 'status',
      sortable: true,
      statusType: (row: EmployeeListing) =>
        row.status === 'Active' ? 'success' : 'error',
      statusIcon: (row: EmployeeListing) =>
        row.status === 'Active' ? 'check_circle' : 'cancel',
    },
  ];

  actions: TableAction<EmployeeListing>[] = [
    {
      icon: 'visibility',
      tooltip: 'View Details',
      action: 'view',
      permission: 'employee.read',
    },
    {
      icon: 'edit',
      tooltip: 'Edit Employee',
      action: 'edit',
      permission: 'employee.update',
    },
    {
      icon: 'delete',
      tooltip: 'Delete Employee',
      action: 'delete',
      color: 'warn',
      permission: 'employee.delete',
      disabled: (row: EmployeeListing) => !row._employee.allow_delete,
    },
  ];

  searchForm: FormGroup;
  isLoading = false;

  constructor() {
    this.searchForm = this.fb.group({
      badgeNumber: [''],
      firstName: [''],
      lastName: [''],
      department: [''],
      org_unit: [''],
      status: [''],
    });
  }

  ngOnInit() {
    this.loadEmployees();
    this.loadFormData();
    this.setupSearchForm();
  }

  private loadFormData() {
    // Load departments
    this.departmentService.getDepartments().subscribe({
      next: (departments) => {
        this.departments = departments;
      },
      error: (error) => {
        console.error('Error loading departments:', error);
      },
    });

    // Load org units (exclude 'root' org unit)
    this.orgUnitService.getOrgUnits().subscribe({
      next: (orgUnits) => {
        this.orgUnits = orgUnits.filter(ou => ou.name.toLowerCase() !== 'root');
      },
      error: (error) => {
        console.error('Error loading org units:', error);
      },
    });

    // Load holiday groups
    this.holidayGroupService.getHolidayGroups().subscribe({
      next: (holidayGroups) => {
        this.holidayGroups = holidayGroups;
      },
      error: (error) => {
        console.error('Error loading holiday groups:', error);
      },
    });

    // Load managers (employees who can be managers)
    this.employeeService.getEmployees().subscribe({
      next: (employees) => {
        // Filter out root employee (id=0)
        this.managers = employees.filter(emp => emp.id !== 0);
      },
      error: (error) => {
        console.error('Error loading managers:', error);
      },
    });
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.loadEmployees();
    });
  }

  loadEmployees() {
    this.isLoading = true;
    
    const formValue = this.searchForm.value;
    
    this.employeeService
      .getEmployeesByCriteria(
        formValue.department || undefined,
        formValue.org_unit || undefined,
        undefined, // holiday_group_name
        formValue.badgeNumber || undefined,
        formValue.firstName || undefined,
        formValue.lastName || undefined
      )
      .subscribe({
        next: (employees) => {
          // Filter out root employee (id=0) and transform to EmployeeListing
          const listings = employees
            .filter(emp => emp.id !== 0)
            .map(emp => this.transformToListing(emp));
          this.dataSource.data = listings;
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to load employees', error);
          this.isLoading = false;
        },
      });
  }

  private transformToListing(emp: Employee): EmployeeListing {
    return {
      id: emp.id!,
      badge_number: emp.badge_number,
      name: `${emp.first_name} ${emp.last_name}`,
      payroll_type: emp.payroll_type || '',
      org_unit: emp.org_unit?.name || '',
      departments: emp.departments?.map(d => d.name).join(', ') || '',
      holiday_group: emp.holiday_group?.name || '',
      status: emp.allow_clocking ? 'Active' : 'Inactive',
      _employee: emp,
    };
  }

  onTableAction(event: TableActionEvent<EmployeeListing>) {
    switch (event.action) {
      case 'view':
        this.viewEmployee(event.row._employee);
        break;
      case 'edit':
        this.editEmployee(event.row._employee);
        break;
      case 'delete':
        this.deleteEmployee(event.row._employee);
        break;
    }
  }

  addEmployee() {
    const dialogRef = this.dialog.open(EmployeeFormDialogComponent, {
      width: '900px',
      data: {
        departments: this.departments,
        orgUnits: this.orgUnits,
        holidayGroups: this.holidayGroups,
        managers: this.managers,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const newListing = this.transformToListing(result);
        this.dataSource.data = [...this.dataSource.data, newListing];
        this.showSnackBar(
          `Employee "${result.first_name} ${result.last_name}" created successfully`,
          'success'
        );
      }
    });
  }

  editEmployee(employee: Employee) {
    const dialogRef = this.dialog.open(EmployeeFormDialogComponent, {
      width: '900px',
      data: {
        editEmployee: employee,
        departments: this.departments,
        orgUnits: this.orgUnits,
        holidayGroups: this.holidayGroups,
        managers: this.managers,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const index = this.dataSource.data.findIndex((listing) => listing.id === employee.id);
        if (index > -1) {
          const updatedListing = this.transformToListing(result);
          const newData = [...this.dataSource.data];
          newData[index] = updatedListing;
          this.dataSource.data = newData;
          this.showSnackBar('Employee updated successfully', 'success');
        }
      }
    });
  }



  viewEmployee(employee: Employee) {
    const dialogRef = this.dialog.open(EmployeeDetailsDialogComponent, {
      width: '700px',
      data: { employee },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'edit') {
        this.editEmployee(result.employee);
      } else if (result?.action === 'delete') {
        this.deleteEmployee(result.employee);
      }
    });
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

      this.employeeService.deleteEmployee(employee.id!).subscribe({
        next: () => {
          this.dataSource.data = this.dataSource.data.filter(
            (listing) => listing.id !== employee.id
          );
          this.showSnackBar(
            `${employee.first_name} ${employee.last_name} has been deleted successfully`,
            'success'
          );
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to delete employee', error);
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
        error: extractErrorDetail(error),
      },
    });
  }
}
