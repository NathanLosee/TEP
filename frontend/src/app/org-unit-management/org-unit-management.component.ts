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
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { OrgUnitService, OrgUnit, OrgUnitWithEmployees } from '../../services/org-unit.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

@Component({
  selector: 'app-org-unit-management',
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
    MatSelectModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './org-unit-management.component.html',
  styleUrl: './org-unit-management.component.scss',
})
export class OrgUnitManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private orgUnitService = inject(OrgUnitService);

  orgUnits: OrgUnit[] = [];
  filteredOrgUnits: OrgUnit[] = [];
  selectedOrgUnitDetails: OrgUnitWithEmployees | null = null;
  displayedColumns: string[] = ['name', 'employee_count', 'actions'];

  searchForm: FormGroup;
  addOrgUnitForm: FormGroup;
  editForm: FormGroup;
  isLoading = false;
  showAddForm = false;
  showEditForm = false;
  showEmployeeList = false;
  selectedOrgUnit: OrgUnit | null = null;

  constructor() {
    this.searchForm = this.fb.group({
      searchTerm: [''],
      location: [''],
    });

    this.addOrgUnitForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      description: [''],
    });

    this.editForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      description: [''],
    });
  }

  ngOnInit() {
    this.loadOrgUnits();
    this.setupSearchForm();
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterOrgUnits();
    });
  }

  loadOrgUnits() {
    this.isLoading = true;
    this.orgUnitService.getOrgUnits().subscribe({
      next: (orgUnits) => {
        this.orgUnits = orgUnits;
        this.filteredOrgUnits = [...this.orgUnits];
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load organizational units', error);
        this.isLoading = false;
      }
    });
  }

  filterOrgUnits() {
    const filters = this.searchForm.value;

    this.filteredOrgUnits = this.orgUnits.filter((unit) => {
      const searchTerm = filters.searchTerm?.toLowerCase() || '';
      const matchesSearch =
        !searchTerm || unit.name.toLowerCase().includes(searchTerm);

      return matchesSearch;
    });
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.addOrgUnitForm.reset();
    }
  }

  addOrgUnit() {
    if (this.addOrgUnitForm.valid) {
      const formValue = this.addOrgUnitForm.value;
      const newOrgUnit: OrgUnit = {
        id: this.orgUnits.length + 1,
        name: formValue.name,
        employee_count: 0,
      };

      this.orgUnits.push(newOrgUnit);
      this.filterOrgUnits();
      this.addOrgUnitForm.reset();
      this.showAddForm = false;
      this.showSnackBar(
        `Org Unit "${newOrgUnit.name}" created successfully`,
        'success'
      );
    }
  }

  // Action methods for buttons
  viewEmployees(orgUnit: OrgUnit) {
    this.selectedOrgUnit = orgUnit;
    this.showEmployeeList = true;
    this.showEditForm = false;
  }

  editOrgUnit(orgUnit: OrgUnit) {
    this.selectedOrgUnit = orgUnit;
    this.showEditForm = true;
    this.showEmployeeList = false;

    // Initialize edit form with org unit data
    this.editForm.patchValue({
      name: orgUnit.name,
      description: orgUnit.description || '',
    });
  }

  deleteOrgUnit(orgUnit: OrgUnit) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${orgUnit.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      // Remove org unit from the array (simulating API call)
      setTimeout(() => {
        const index = this.orgUnits.findIndex((unit) => unit.id === orgUnit.id);
        if (index > -1) {
          this.orgUnits.splice(index, 1);
          this.filterOrgUnits();
          this.showSnackBar(
            `${orgUnit.name} has been deleted successfully`,
            'success'
          );
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  saveOrgUnit() {
    if (this.editForm && this.editForm.valid && this.selectedOrgUnit) {
      this.isLoading = true;

      const formData = this.editForm.value;

      // Update org unit data (simulating API call)
      setTimeout(() => {
        const index = this.orgUnits.findIndex(
          (unit) => unit.id === this.selectedOrgUnit!.id
        );
        if (index > -1) {
          this.orgUnits[index] = {
            ...this.orgUnits[index],
            name: formData.name,
            description: formData.description,
          };
          this.filterOrgUnits();
          this.showSnackBar('Org Unit updated successfully', 'success');
          this.cancelAction();
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  cancelAction() {
    this.showEditForm = false;
    this.showEmployeeList = false;
    this.selectedOrgUnit = null;
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

  private generateMockOrgUnits(): OrgUnit[] {
    return [
      {
        id: 1,
        name: 'Corporate Office',
        employee_count: 15,
      },
      {
        id: 2,
        name: 'Manufacturing Plant',
        employee_count: 25,
      },
      {
        id: 3,
        name: 'IT Department',
        employee_count: 12,
      },
      {
        id: 4,
        name: 'Quality Control',
        employee_count: 8,
      },
      {
        id: 5,
        name: 'Sales & Marketing',
        employee_count: 10,
      },
      {
        id: 6,
        name: 'Research & Development',
        employee_count: 18,
      },
    ];
  }
}
