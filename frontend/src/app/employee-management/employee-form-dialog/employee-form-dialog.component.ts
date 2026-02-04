import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  Department,
  DepartmentService,
} from '../../../services/department.service';
import { Employee, EmployeeService } from '../../../services/employee.service';
import {
  HolidayGroup,
  HolidayGroupService,
} from '../../../services/holiday-group.service';
import { OrgUnit, OrgUnitService } from '../../../services/org-unit.service';
import { ManagerSearchDialogComponent } from '../manager-search-dialog/manager-search-dialog.component';

export interface EmployeeFormDialogData {
  editEmployee?: Employee | null;
  departments?: Department[];
  orgUnits?: OrgUnit[];
  holidayGroups?: HolidayGroup[];
  managers?: Employee[];
}

@Component({
  selector: 'app-employee-form-dialog',
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
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatSelectModule,
    MatCheckboxModule,
    MatTooltipModule,
  ],
  templateUrl: './employee-form-dialog.component.html',
  styleUrl: './employee-form-dialog.component.scss',
})
export class EmployeeFormDialogComponent {
  private fb = inject(FormBuilder);
  private employeeService = inject(EmployeeService);
  private departmentService = inject(DepartmentService);
  private orgUnitService = inject(OrgUnitService);
  private holidayGroupService = inject(HolidayGroupService);
  private dialogRef = inject(MatDialogRef<EmployeeFormDialogComponent>);
  private dialog = inject(MatDialog);
  public data = inject(MAT_DIALOG_DATA) as EmployeeFormDialogData;

  employeeForm!: FormGroup;
  isLoading = false;
  isEditMode = false;

  departments: Department[] = [];
  orgUnits: OrgUnit[] = [];
  holidayGroups: HolidayGroup[] = [];
  managers: Employee[] = [];

  // Selected manager for display
  selectedManager: Employee | null = null;

  constructor() {
    this.isEditMode = !!this.data.editEmployee;
    this.initializeForm();
    this.loadFormData();
    this.initializeSelectedManager();
  }

  private initializeSelectedManager() {
    if (this.data.editEmployee?.manager) {
      this.selectedManager = this.data.editEmployee.manager;
    }
  }

  private initializeForm() {
    this.employeeForm = this.fb.group({
      badge_number: [
        this.data.editEmployee?.badge_number || '',
        [Validators.required],
      ],
      first_name: [
        this.data.editEmployee?.first_name || '',
        [Validators.required],
      ],
      last_name: [
        this.data.editEmployee?.last_name || '',
        [Validators.required],
      ],
      payroll_type: [
        this.data.editEmployee?.payroll_type || 'hourly',
        [Validators.required],
      ],
      payroll_sync: [this.data.editEmployee?.payroll_sync || null],
      workweek_type: [
        this.data.editEmployee?.workweek_type || 'standard',
        [Validators.required],
      ],
      time_type: [this.data.editEmployee?.time_type || true],
      allow_clocking: [this.data.editEmployee?.allow_clocking || true],
      external_clock_allowed: [
        this.data.editEmployee?.external_clock_allowed || false,
      ],
      allow_delete: [this.data.editEmployee?.allow_delete || true],
      holiday_group_id: [this.data.editEmployee?.holiday_group?.id || null],
      org_unit_id: [
        this.data.editEmployee?.org_unit?.id || null,
        [Validators.required],
      ],
      manager_id: [this.data.editEmployee?.manager?.id || null],
    });
  }

  private loadFormData() {
    this.departments = this.data.departments || [];
    this.orgUnits = this.data.orgUnits || [];
    this.holidayGroups = this.data.holidayGroups || [];
    this.managers = this.data.managers || [];
  }

  submitForm() {
    if (this.employeeForm.valid) {
      this.isLoading = true;

      const employeeData = {
        ...this.employeeForm.value,
        payroll_sync:
          typeof this.employeeForm.get('payroll_sync')?.value === 'string'
            ? this.employeeForm.get('payroll_sync')?.value
            : this.employeeForm
                .get('payroll_sync')
                ?.value?.toISOString()
                .split('T')[0],
      };

      if (this.isEditMode && this.data.editEmployee) {
        this.employeeService
          .updateEmployee(this.data.editEmployee.id!, employeeData)
          .subscribe({
            next: (updatedEmployee) => {
              this.dialogRef.close(updatedEmployee);
              this.isLoading = false;
            },
            error: (error) => {
              console.error('Error updating employee:', error);
              this.isLoading = false;
            },
          });
      } else {
        this.employeeService.createEmployee(employeeData).subscribe({
          next: (newEmployee) => {
            this.dialogRef.close(newEmployee);
            this.isLoading = false;
          },
          error: (error) => {
            console.error('Error creating employee:', error);
            this.isLoading = false;
          },
        });
      }
    }
  }

  cancelForm() {
    this.dialogRef.close();
  }

  openManagerSearch() {
    const dialogRef = this.dialog.open(ManagerSearchDialogComponent, {
      width: '500px',
      data: {
        managers: this.managers,
        currentManagerId: this.employeeForm.get('manager_id')?.value,
      },
    });

    dialogRef.afterClosed().subscribe((result: Employee | null | undefined) => {
      if (result !== undefined) {
        // result can be null (no manager) or an Employee
        this.selectedManager = result;
        this.employeeForm.patchValue({
          manager_id: result?.id || null,
        });
      }
    });
  }

  clearManager() {
    this.selectedManager = null;
    this.employeeForm.patchValue({
      manager_id: null,
    });
  }
}
