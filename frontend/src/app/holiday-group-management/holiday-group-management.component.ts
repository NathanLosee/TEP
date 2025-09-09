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
import { PartialObserver } from 'rxjs';
import {
  HolidayGroup,
  HolidayGroupService,
} from '../../services/holiday-group.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { HolidayFormComponent } from './holiday-form/holiday-form.component';
import { HolidayGroupDetailsDialogComponent } from './holiday-group-details-dialog/holiday-group-details-dialog.component';

@Component({
  selector: 'app-holiday-group-management',
  standalone: true,
  imports: [
    HolidayFormComponent,
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatDatepickerModule,
    MatDialogModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTableModule,
    MatTabsModule,
    MatTooltipModule,
    ReactiveFormsModule,
  ],
  templateUrl: './holiday-group-management.component.html',
  styleUrl: './holiday-group-management.component.scss',
})
export class HolidayGroupManagementComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private errorDialog = inject(ErrorDialogComponent);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);

  private holidayGroupService = inject(HolidayGroupService);
  private holidayFormComponent = new HolidayFormComponent();

  // Data
  holidayGroups: HolidayGroup[] = [];
  filteredGroups: HolidayGroup[] = [];
  selectedGroup: HolidayGroup | null = null;

  // Forms
  searchForm: FormGroup;
  holidayForm: FormGroup;

  // UI State
  isLoading = false;
  showForm = false;
  showEmployeeList = false;

  // Table columns
  displayedColumns: string[] = ['name', 'holidays_count', 'actions'];

  constructor() {
    this.searchForm = this.formBuilder.group({
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
        holidayGroups.forEach((group) => {
          group.holidays = group.holidays.map((holiday) => ({
            ...holiday,
            start_date: new Date(holiday.start_date),
            end_date: new Date(holiday.end_date),
          }));
        });
        this.holidayGroups = holidayGroups;
        this.filterGroups();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog(
          'Failed to load holiday groups',
          error
        );
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
    const searchTerm =
      this.searchForm.get('name')?.value?.toLowerCase().trim() || '';

    if (!searchTerm) {
      this.filteredGroups = [...this.holidayGroups];
      return;
    }
    this.filteredGroups = this.holidayGroups.filter((group) =>
      group.name.toLowerCase().includes(searchTerm)
    );
  }

  viewEmployees(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showEmployeeList = true;
    this.showForm = false;

    this.holidayGroupService.getEmployeesByHolidayGroup(group.id!).subscribe({
      next: (employees) => {
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog(
          'Failed to load holiday group employees',
          error
        );
        this.isLoading = false;
      },
    });
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.holidayFormComponent.resetForm();
    }
  }

  editGroup(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showForm = true;
    this.showEmployeeList = false;
    this.holidayFormComponent.patchForm(group);
  }

  cancelAction() {
    this.showForm = false;
    this.showEmployeeList = false;
    this.selectedGroup = null;
  }

  viewHolidayDetails(group: HolidayGroup) {
    this.dialog.open(HolidayGroupDetailsDialogComponent, {
      width: '600px',
      data: { holidayGroup: group },
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });
  }

  saveHolidayGroup(holidayGroupData: HolidayGroup) {
    this.holidayFormComponent.isLoading = true;
    console.log('Saving holiday group:', holidayGroupData);
    const observer: PartialObserver<HolidayGroup> = {
      next: (returnedGroup) => {
        if (this.selectedGroup) {
          // Replace existing group
          const index = this.holidayGroups.findIndex(
            (g) => g.id === this.selectedGroup!.id
          );
          if (index > -1) {
            this.holidayGroups[index] = returnedGroup;
          }
        } else {
          // Add new group
          this.holidayGroups.push(returnedGroup);
        }
        this.filterGroups();
        this.showSnackBar('Holiday Group updated successfully', 'success');
        this.holidayFormComponent.resetForm();
        this.cancelAction();
        this.holidayFormComponent.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog(
          'Failed to update holiday group',
          error
        );
        this.holidayFormComponent.isLoading = false;
      },
    };

    if (this.selectedGroup) {
      // Editing an existing group
      this.holidayGroupService
        .updateHolidayGroup(this.selectedGroup.id!, holidayGroupData)
        .subscribe(observer);
    } else {
      // Creating a new group
      this.holidayGroupService
        .createHolidayGroup(holidayGroupData)
        .subscribe(observer);
    }
  }

  deleteGroup(group: HolidayGroup) {
    if (
      confirm(
        `Are you sure you want to delete "${group.name}"? This action cannot be undone.`
      )
    ) {
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
          this.errorDialog.openErrorDialog(
            'Failed to delete holiday group',
            error
          );
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
}
