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
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTabsModule } from '@angular/material/tabs';
import { HolidayGroupService, HolidayGroup, Holiday, HolidayGroupWithDetails } from '../../services/holiday-group.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

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
  ],
  templateUrl: './holiday-group-management.component.html',
  styleUrl: './holiday-group-management.component.scss',
})
export class HolidayGroupManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private holidayGroupService = inject(HolidayGroupService);

  holidayGroups: HolidayGroup[] = [];
  filteredGroups: HolidayGroup[] = [];
  selectedGroupDetails: HolidayGroupWithDetails | null = null;
  displayedColumns: string[] = [
    'name',
    'holidays_count', 
    'actions',
  ];

  searchForm: FormGroup;
  addGroupForm: FormGroup;
  addHolidayForm: FormGroup;
  editForm: FormGroup;
  isLoading = false;
  showAddForm = false;
  showEditForm = false;
  showEmployeeList = false;
  selectedGroup: HolidayGroup | null = null;

  constructor() {
    this.searchForm = this.fb.group({
      searchTerm: [''],
    });

    this.addGroupForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
    });

    this.addHolidayForm = this.fb.group({
      name: ['', [Validators.required]],
      start_date: [null, [Validators.required]],
      end_date: [null, [Validators.required]],
    });

    this.editForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
    });
  }

  ngOnInit() {
    this.loadHolidayGroups();
    this.setupSearchForm();
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
        this.holidayGroups = holidayGroups;
        this.filteredGroups = [...this.holidayGroups];
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load holiday groups', error);
        this.isLoading = false;
      }
    });
  }

  filterGroups() {
    const searchTerm =
      this.searchForm.get('searchTerm')?.value?.toLowerCase() || '';

    this.filteredGroups = this.holidayGroups.filter((group) =>
      group.name.toLowerCase().includes(searchTerm)
    );
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.addGroupForm.reset();
    }
  }

  addHolidayGroup() {
    if (this.addGroupForm.valid) {
      this.isLoading = true;
      const holidayGroupData = {
        name: this.addGroupForm.get('name')?.value
      };

      this.holidayGroupService.createHolidayGroup(holidayGroupData).subscribe({
        next: (newGroup) => {
          this.holidayGroups.push(newGroup);
          this.filterGroups();
          this.addGroupForm.reset();
          this.showAddForm = false;
          this.showSnackBar(
            `Holiday Group "${newGroup.name}" created successfully`,
            'success'
          );
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to create holiday group', error);
          this.isLoading = false;
        }
      });
    }
  }

  addHoliday(groupId: number) {
    if (this.addHolidayForm.valid) {
      const startDate = this.addHolidayForm.get('start_date')?.value;
      const endDate = this.addHolidayForm.get('end_date')?.value;
      
      const holidayData = {
        name: this.addHolidayForm.get('name')?.value,
        start_date: startDate?.toISOString().split('T')[0],
        end_date: endDate?.toISOString().split('T')[0],
      };

      this.holidayGroupService.addHoliday(groupId, holidayData).subscribe({
        next: (newHoliday) => {
          this.showSnackBar(
            `Holiday "${newHoliday.name}" added successfully`,
            'success'
          );
          this.addHolidayForm.reset();
          // Reload the group details if we're viewing them
          if (this.selectedGroup?.id === groupId) {
            this.loadGroupDetails(groupId);
          }
        },
        error: (error) => {
          this.handleError('Failed to add holiday', error);
        }
      });
    }
  }

  loadGroupDetails(groupId: number) {
    this.holidayGroupService.getHolidayGroupById(groupId).subscribe({
      next: (groupDetails) => {
        this.selectedGroupDetails = groupDetails;
      },
      error: (error) => {
        this.handleError('Failed to load group details', error);
      }
    });
  }

  editGroup(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showEditForm = true;
    this.showEmployeeList = false;

    this.editForm.patchValue({
      name: group.name,
    });
  }

  deleteGroup(group: HolidayGroup) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${group.name}? This action cannot be undone.`
    );

    if (confirmDelete) {
      this.isLoading = true;

      this.holidayGroupService.deleteHolidayGroup(group.id).subscribe({
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
        }
      });
    }
  }

  viewEmployees(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showEmployeeList = true;
    this.showEditForm = false;
    this.loadGroupDetails(group.id);
  }

  saveGroup() {
    if (this.editForm && this.editForm.valid && this.selectedGroup) {
      this.isLoading = true;

      const holidayGroupData = {
        name: this.editForm.get('name')?.value
      };

      this.holidayGroupService.updateHolidayGroup(this.selectedGroup.id, holidayGroupData).subscribe({
        next: (updatedGroup) => {
          const index = this.holidayGroups.findIndex(
            (g) => g.id === this.selectedGroup!.id
          );
          if (index > -1) {
            this.holidayGroups[index] = updatedGroup;
            this.filterGroups();
            this.showSnackBar('Holiday Group updated successfully', 'success');
            this.cancelAction();
          }
          this.isLoading = false;
        },
        error: (error) => {
          this.handleError('Failed to update holiday group', error);
          this.isLoading = false;
        }
      });
    }
  }

  cancelAction() {
    this.showEditForm = false;
    this.showEmployeeList = false;
    this.selectedGroup = null;
    this.selectedGroupDetails = null;
    this.editForm?.reset();
  }

  removeHoliday(groupId: number, holidayName: string) {
    this.holidayGroupService.deleteHoliday(groupId, holidayName).subscribe({
      next: () => {
        this.showSnackBar('Holiday removed successfully', 'success');
        // Reload group details
        if (this.selectedGroup?.id === groupId) {
          this.loadGroupDetails(groupId);
        }
      },
      error: (error) => {
        this.handleError('Failed to remove holiday', error);
      }
    });
  }

  exportHolidaySchedule() {
    this.showSnackBar('Exporting holiday schedule...', 'info');
    setTimeout(() => {
      this.showSnackBar('Holiday schedule exported successfully', 'success');
    }, 1500);
  }

  importHolidays() {
    this.showSnackBar('Import holidays feature coming soon', 'info');
  }

  getUpcomingHolidays() {
    if (!this.selectedGroupDetails?.holidays) return [];
    
    const today = new Date();
    return this.selectedGroupDetails.holidays
      .filter((holiday) => new Date(holiday.start_date) >= today)
      .sort((a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime())
      .slice(0, 5);
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
        error: error?.error?.detail || error?.message || 'Unknown error'
      }
    });
  }
}
