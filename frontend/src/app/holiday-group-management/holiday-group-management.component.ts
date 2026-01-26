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
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PartialObserver } from 'rxjs';
import {
  HolidayGroup,
  HolidayGroupService,
} from '../../services/holiday-group.service';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../shared/models/table.models';
import { HolidayFormDialogComponent } from './holiday-form-dialog/holiday-form-dialog.component';
import { HolidayGroupDetailsDialogComponent } from './holiday-group-details-dialog/holiday-group-details-dialog.component';
import { HolidayGroupEmployeesDialogComponent } from './holiday-group-employees-dialog/holiday-group-employees-dialog.component';

@Component({
  selector: 'app-holiday-group-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSnackBarModule,
    MatTabsModule,
    MatTooltipModule,
    DisableIfNoPermissionDirective,
    GenericTableComponent,
    TableCellDirective,
  ],
  templateUrl: './holiday-group-management.component.html',
  styleUrl: './holiday-group-management.component.scss',
})
export class HolidayGroupManagementComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);

  private holidayGroupService = inject(HolidayGroupService);

  // Data
  holidayGroups: HolidayGroup[] = [];
  filteredGroups: HolidayGroup[] = [];
  selectedGroup: HolidayGroup | null = null;

  // Forms
  searchForm: FormGroup;

  // UI State
  isLoading = false;

  // Table configuration
  columns: TableColumn<HolidayGroup>[] = [
    {
      key: 'name',
      header: 'Group Name',
      type: 'icon-text',
      icon: 'event',
    },
    {
      key: 'holidays_count',
      header: 'Holidays',
      type: 'template',
    },
  ];

  actions: TableAction<HolidayGroup>[] = [
    {
      icon: 'visibility',
      tooltip: 'View Details',
      action: 'viewDetails',
      permission: 'holiday_group.read',
    },
    {
      icon: 'people',
      tooltip: 'View Employees',
      action: 'viewEmployees',
      permission: 'holiday_group.read',
    },
    {
      icon: 'edit',
      tooltip: 'Edit Group',
      action: 'edit',
      color: 'primary',
      permission: 'holiday_group.update',
    },
    {
      icon: 'delete',
      tooltip: 'Delete Group',
      action: 'delete',
      color: 'warn',
      permission: 'holiday_group.delete',
      disabled: (group: HolidayGroup) => (group.employee_count || 0) > 0,
    },
  ];

  constructor() {
    this.searchForm = this.formBuilder.group({
      name: [''],
    });
  }

  ngOnInit() {
    this.setupSearchForm();
    this.loadHolidayGroups();
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterGroups();
    });
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
        this.handleError('Failed to load holiday groups', error);
        this.isLoading = false;
      },
    });
  }

  filterGroups() {
    const filters = this.searchForm.value;

    if (!filters.name) {
      this.filteredGroups = [...this.holidayGroups];
      return;
    }
    this.filteredGroups = this.holidayGroups.filter((group) => {
      const searchName = filters.name?.toLowerCase() || '';
      const matchesSearch =
        !searchName || group.name.toLowerCase().includes(searchName);

      return matchesSearch;
    });
  }

  onTableAction(event: TableActionEvent<HolidayGroup>) {
    switch (event.action) {
      case 'viewDetails':
        this.viewHolidayDetails(event.row);
        break;
      case 'viewEmployees':
        this.viewEmployees(event.row);
        break;
      case 'edit':
        this.openHolidayFormDialog(event.row);
        break;
      case 'delete':
        this.deleteGroup(event.row);
        break;
    }
  }

  viewEmployees(group: HolidayGroup) {
    this.dialog.open(HolidayGroupEmployeesDialogComponent, {
      width: '800px',
      maxWidth: '90vw',
      data: { holidayGroup: group },
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });
  }

  openHolidayFormDialog(editGroup?: HolidayGroup) {
    const dialogRef = this.dialog.open(HolidayFormDialogComponent, {
      width: '700px',
      maxWidth: '90vw',
      data: { editGroup },
      disableClose: true,
      enterAnimationDuration: 250,
      exitAnimationDuration: 250,
    });

    dialogRef.afterClosed().subscribe((result: HolidayGroup | undefined) => {
      if (result) {
        this.saveHolidayGroup(result);
      }
    });
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
    this.isLoading = true;
    if (this.selectedGroup) {
      holidayGroupData.id = this.selectedGroup.id;
    }
    console.log('Saving holiday group:', holidayGroupData);
    const observer: PartialObserver<HolidayGroup> = {
      next: (returnedGroup) => {
        // Ensure dates are properly parsed as Date objects
        returnedGroup.holidays = returnedGroup.holidays.map((holiday) => ({
          ...holiday,
          start_date: new Date(holiday.start_date),
          end_date: new Date(holiday.end_date),
        }));

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
        this.selectedGroup = null;
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to update holiday group', error);
        this.isLoading = false;
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
