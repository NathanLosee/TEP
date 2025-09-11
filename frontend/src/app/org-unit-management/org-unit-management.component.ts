import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { OrgUnit, OrgUnitService } from '../../services/org-unit.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { OrgUnitFormDialogComponent } from './org-unit-management-form-dialog/org-unit-form-dialog.component';

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
    MatTabsModule,
  ],
  templateUrl: './org-unit-management.component.html',
  styleUrl: './org-unit-management.component.scss',
})
export class OrgUnitManagementComponent implements OnInit {
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private orgUnitService = inject(OrgUnitService);
  private fb = inject(FormBuilder);

  orgUnits: OrgUnit[] = [];
  filteredOrgUnits: OrgUnit[] = [];
  displayedColumns: string[] = ['name', 'employee_count', 'actions'];

  searchForm: FormGroup;
  isLoading = false;

  constructor() {
    this.searchForm = this.fb.group({
      searchTerm: [''],
      location: [''],
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
      },
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

  addOrgUnit() {
    const dialogRef = this.dialog.open(OrgUnitFormDialogComponent, {
      width: '600px',
      data: {
        orgUnits: this.orgUnits, // For parent org unit selection
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.orgUnits.push(result);
        this.filterOrgUnits();
        this.showSnackBar(
          `Org Unit "${result.name}" created successfully`,
          'success'
        );
      }
    });
  }

  editOrgUnit(orgUnit: OrgUnit) {
    const dialogRef = this.dialog.open(OrgUnitFormDialogComponent, {
      width: '600px',
      data: {
        editOrgUnit: orgUnit,
        orgUnits: this.orgUnits,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const index = this.orgUnits.findIndex((unit) => unit.id === orgUnit.id);
        if (index > -1) {
          this.orgUnits[index] = result;
          this.filterOrgUnits();
          this.showSnackBar('Organizational unit updated successfully', 'success');
        }
      }
    });
  }

  deleteOrgUnit(orgUnit: OrgUnit) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${orgUnit.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      this.orgUnitService.deleteOrgUnit(orgUnit.id!).subscribe({
        next: () => {
          const index = this.orgUnits.findIndex(
            (unit) => unit.id === orgUnit.id
          );
          if (index > -1) {
            this.orgUnits.splice(index, 1);
            this.filterOrgUnits();
            this.showSnackBar(
              `${orgUnit.name} has been deleted successfully`,
              'success'
            );
          }
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to delete organizational unit', error);
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
