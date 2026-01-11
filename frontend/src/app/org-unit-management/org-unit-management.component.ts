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
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PartialObserver } from 'rxjs';
import { OrgUnit, OrgUnitService } from '../../services/org-unit.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { OrgUnitEmployeesDialogComponent } from './org-unit-employees-dialog/org-unit-employees-dialog.component';
import { OrgUnitFormDialogComponent } from './org-unit-form-dialog/org-unit-form-dialog.component';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';

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
    DisableIfNoPermissionDirective,
  ],
  templateUrl: './org-unit-management.component.html',
  styleUrl: './org-unit-management.component.scss',
})
export class OrgUnitManagementComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);

  private orgUnitService = inject(OrgUnitService);

  // Data
  orgUnits: OrgUnit[] = [];
  filteredOrgUnits: OrgUnit[] = [];
  selectedUnit: OrgUnit | null = null;

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
    this.loadOrgUnits();
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
        // Filter out the root org unit (id=0)
        this.orgUnits = orgUnits.filter(unit => unit.id !== 0);
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

    if (!filters.name) {
      this.filteredOrgUnits = [...this.orgUnits];
      return;
    }
    this.filteredOrgUnits = this.orgUnits.filter((unit) => {
      const searchName = filters.name?.toLowerCase() || '';
      const matchesSearch =
        !searchName || unit.name.toLowerCase().includes(searchName);

      return matchesSearch;
    });
  }

  viewEmployees(unit: OrgUnit) {
    this.dialog.open(OrgUnitEmployeesDialogComponent, {
      width: '800px',
      maxWidth: '90vw',
      data: { orgUnit: unit },
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });
  }

  openOrgUnitFormDialog(editUnit?: OrgUnit) {
    const dialogRef = this.dialog.open(OrgUnitFormDialogComponent, {
      width: '700px',
      maxWidth: '90vw',
      data: { editUnit },
      disableClose: true,
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });

    dialogRef.afterClosed().subscribe((result: OrgUnit | undefined) => {
      if (result) {
        this.saveOrgUnit(result);
      }
    });
  }

  saveOrgUnit(orgUnitData: OrgUnit) {
    this.isLoading = true;
    if (this.selectedUnit) {
      orgUnitData.id = this.selectedUnit.id;
    }
    console.log('Saving organizational unit:', orgUnitData);
    const observer: PartialObserver<OrgUnit> = {
      next: (returnedUnit) => {
        if (this.selectedUnit) {
          // Replace existing unit
          const index = this.orgUnits.findIndex(
            (u) => u.id === this.selectedUnit!.id
          );
          if (index > -1) {
            this.orgUnits[index] = returnedUnit;
          }
        } else {
          // Add new unit
          this.orgUnits.push(returnedUnit);
        }
        this.filterOrgUnits();
        this.showSnackBar(
          'Organizational Unit updated successfully',
          'success'
        );
        this.selectedUnit = null;
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to update organizational unit', error);
        this.isLoading = false;
      },
    };

    if (this.selectedUnit) {
      // Editing an existing unit
      this.orgUnitService
        .updateOrgUnit(this.selectedUnit.id!, orgUnitData)
        .subscribe(observer);
    } else {
      // Creating a new unit
      this.orgUnitService.createOrgUnit(orgUnitData).subscribe(observer);
    }
  }

  deleteOrgUnit(unit: OrgUnit) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${unit.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      this.orgUnitService.deleteOrgUnit(unit.id!).subscribe({
        next: () => {
          const index = this.orgUnits.findIndex((u) => u.id === unit.id);
          if (index > -1) {
            this.orgUnits.splice(index, 1);
            this.filterOrgUnits();
            this.showSnackBar(
              `${unit.name} has been deleted successfully`,
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
