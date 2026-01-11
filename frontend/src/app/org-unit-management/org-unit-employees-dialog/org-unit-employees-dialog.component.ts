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
import { OrgUnit, OrgUnitService } from '../../../services/org-unit.service';
import { ErrorDialogComponent } from '../../error-dialog/error-dialog.component';

export interface OrgUnitEmployeesDialogData {
  orgUnit: OrgUnit;
}

@Component({
  selector: 'app-org-unit-employees-dialog',
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
  templateUrl: './org-unit-employees-dialog.component.html',
  styleUrl: './org-unit-employees-dialog.component.scss',
})
export class OrgUnitEmployeesDialogComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private orgUnitService = inject(OrgUnitService);
  private errorDialog = inject(ErrorDialogComponent);
  readonly data = inject<OrgUnitEmployeesDialogData>(MAT_DIALOG_DATA);

  employees: Employee[] = [];
  filteredEmployees: Employee[] = [];
  isLoading = false;
  searchForm: FormGroup;

  // Table columns
  displayedColumns: string[] = ['badge_number', 'first_name', 'last_name'];

  constructor() {
    this.searchForm = this.formBuilder.group({
      badge_number: [''],
      first_name: [''],
      last_name: [''],
    });
  }

  get orgUnit(): OrgUnit {
    return this.data.orgUnit;
  }

  ngOnInit() {
    this.loadEmployees();
    this.setupSearchForm();
  }

  loadEmployees() {
    this.isLoading = true;
    this.orgUnitService.getEmployeesByOrgUnit(this.orgUnit.id!).subscribe({
      next: (employees) => {
        // Filter out root employee (id=0)
        this.employees = employees.filter(emp => emp.id !== 0);
        this.filterEmployees();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog(
          'Failed to load organizational unit employees',
          error
        );
        this.isLoading = false;
      },
    });
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterEmployees();
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
      const badgeNumberMatch =
        !badgeNumberTerm ||
        employee.badge_number.toLowerCase().includes(badgeNumberTerm);
      const firstNameMatch =
        !firstNameTerm ||
        employee.first_name.toLowerCase().includes(firstNameTerm);
      const lastNameMatch =
        !lastNameTerm ||
        employee.last_name.toLowerCase().includes(lastNameTerm);

      return badgeNumberMatch && firstNameMatch && lastNameMatch;
    });
  }

  clearSearch() {
    this.searchForm.reset();
  }
}
