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
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  HolidayGroup,
  HolidayGroupService,
} from '../../services/holiday-group.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { HolidayFormComponent } from './holiday-form/holiday-form.component';

@Component({
  selector: 'app-holiday-group-management',
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
    MatDatepickerModule,
    MatNativeDateModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatTabsModule,
    HolidayFormComponent,
  ],
  templateUrl: './holiday-group-management.component.html',
  styleUrl: './holiday-group-management.component.scss',
})
export class HolidayGroupManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private holidayGroupService = inject(HolidayGroupService);
  private holidayFormComponent = new HolidayFormComponent();

  holidayGroups: HolidayGroup[] = [];
  filteredGroups: HolidayGroup[] = [];
  displayedColumns: string[] = ['name', 'holidays_count', 'actions'];

  searchForm: FormGroup;
  holidayForm: FormGroup;
  isLoading = false;
  showAddForm = false;
  showEditForm = false;
  showEmployeeList = false;
  selectedGroup: HolidayGroup | null = null;

  constructor() {
    this.searchForm = this.fb.group({
      name: [''],
    });

    this.holidayForm = this.holidayFormComponent.holidayForm;
  }

  ngOnInit() {
    this.loadHolidayGroups();
    this.setupSearchForm();
  }

  loadHolidayGroups() {
    this.isLoading = true;
    this.holidayGroupService.getHolidayGroups().subscribe({
      next: (holidayGroups) => {
        this.holidayGroups = holidayGroups;
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load holiday groups', error);
        this.isLoading = false;
      },
    });
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterGroups();
    });
  }

  filterGroups() {
    const searchTerm = this.searchForm.get('name')?.value?.toLowerCase() || '';

    this.filteredGroups = this.holidayGroups.filter((group) =>
      group.name.toLowerCase().includes(searchTerm)
    );
  }

  viewEmployees(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showEmployeeList = true;
    this.showEditForm = false;

    this.holidayGroupService.getEmployeesByHolidayGroup(group.id!).subscribe({
      next: (employees) => {
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load holiday group employees', error);
        this.isLoading = false;
      },
    });
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.holidayFormComponent.resetForm();
    }
  }

  editGroup(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showEditForm = true;
    this.showEmployeeList = false;
    this.holidayFormComponent.patchForm(group);
  }

  cancelAction() {
    this.showAddForm = false;
    this.showEditForm = false;
    this.showEmployeeList = false;
    this.selectedGroup = null;
    this.holidayFormComponent.resetForm();
  }

  saveHolidayGroup(holidayGroupData: HolidayGroup) {
    if (this.holidayForm.valid) {
      this.holidayFormComponent.isLoading = true;

      if (this.showAddForm) {
        this.holidayGroupService
          .createHolidayGroup(holidayGroupData)
          .subscribe({
            next: (newGroup) => {
              this.holidayGroups.push(newGroup);
              this.filterGroups();
              this.holidayFormComponent.resetForm();
              this.showAddForm = false;
              this.showSnackBar(
                `Holiday Group "${newGroup.name}" created successfully`,
                'success'
              );
              this.holidayFormComponent.isLoading = false;
            },
            error: (error) => {
              this.handleError('Failed to create holiday group', error);
              this.holidayFormComponent.isLoading = false;
            },
          });
      } else if (this.showEditForm && this.selectedGroup) {
        this.holidayGroupService
          .updateHolidayGroup(this.selectedGroup.id!, holidayGroupData)
          .subscribe({
            next: (updatedGroup) => {
              const index = this.holidayGroups.findIndex(
                (g) => g.id === this.selectedGroup!.id
              );
              if (index > -1) {
                this.holidayGroups[index] = updatedGroup;
                this.filterGroups();
                this.showSnackBar(
                  'Holiday Group updated successfully',
                  'success'
                );
                this.cancelAction();
              }
              this.holidayFormComponent.isLoading = false;
            },
            error: (error) => {
              this.handleError('Failed to update holiday group', error);
              this.holidayFormComponent.isLoading = false;
            },
          });
      }
    }
  }

  deleteGroup(group: HolidayGroup) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${group.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      this.holidayGroupService.deleteHolidayGroup(group.id!).subscribe({
        next: () => {
          const index = this.holidayGroups.findIndex((g) => g.id === group.id);
          if (index > -1) {
            this.holidayGroups.splice(index, 1);
            this.filterGroups();
            this.showSnackBar(
              `${group.name} has been deleted successfully`,
              'success'
            );
          }
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to delete holiday group', error);
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
