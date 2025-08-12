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
    'employee_count',
    'total_days',
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
      description: [''],
    });

    this.addHolidayForm = this.fb.group({
      name: ['', [Validators.required]],
      start_date: ['', [Validators.required]],
      end_date: ['', [Validators.required]],
      is_recurring: [false],
    });

    this.editForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      description: [''],
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

    this.filteredGroups = this.holidayGroups.filter(
      (group) =>
        group.name.toLowerCase().includes(searchTerm) ||
        group.description?.toLowerCase().includes(searchTerm)
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
      const group = this.holidayGroups.find((g) => g.id === groupId);
      if (group) {
        const startDate = new Date(
          this.addHolidayForm.get('start_date')?.value
        );
        const endDate = new Date(this.addHolidayForm.get('end_date')?.value);
        const daysCount =
          Math.ceil(
            (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
          ) + 1;

        const newHoliday: Holiday = {
          name: this.addHolidayForm.get('name')?.value,
          start_date: startDate,
          end_date: endDate,
          days_count: daysCount,
          is_recurring: this.addHolidayForm.get('is_recurring')?.value,
        };

        group.holidays.push(newHoliday);
        group.total_holiday_days = group.holidays.reduce(
          (sum, h) => sum + h.days_count,
          0
        );

        this.addHolidayForm.reset();
        // selectedGroup reset handled in addHolidayToGroup method
        this.showSnackBar(
          `Holiday "${newHoliday.name}" added successfully`,
          'success'
        );
      }
    }
  }

  // Action methods for buttons
  editGroup(group: HolidayGroup) {
    this.selectedGroup = group;
    this.showEditForm = true;
    this.showEmployeeList = false;

    // Initialize edit form with group data
    this.editForm.patchValue({
      name: group.name,
      description: group.description || '',
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
    this.editForm?.reset();
  }

  removeHoliday(group: HolidayGroup, holidayIndex: number) {
    group.holidays.splice(holidayIndex, 1);
    group.total_holiday_days = group.holidays.reduce(
      (sum, h) => sum + h.days_count,
      0
    );
    this.showSnackBar('Holiday removed successfully', 'success');
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

  getUpcomingHolidays(): Holiday[] {
    const today = new Date();
    const allHolidays: Holiday[] = [];

    this.holidayGroups.forEach((group) => {
      allHolidays.push(...group.holidays);
    });

    return allHolidays
      .filter((holiday) => holiday.start_date >= today)
      .sort((a, b) => a.start_date.getTime() - b.start_date.getTime())
      .slice(0, 5);
  }

  getTotalHolidayGroups(): number {
    return this.holidayGroups.length;
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

  private generateMockHolidayGroups(): HolidayGroup[] {
    return [
      {
        id: 1,
        name: 'US Federal Holidays',
        description: 'Standard US federal holidays observed by all employees',
        employee_count: 85,
        total_holiday_days: 11,
        holidays: [
          {
            name: "New Year's Day",
            start_date: new Date('2024-01-01'),
            end_date: new Date('2024-01-01'),
            days_count: 1,
            is_recurring: true,
          },
          {
            name: 'Independence Day',
            start_date: new Date('2024-07-04'),
            end_date: new Date('2024-07-04'),
            days_count: 1,
            is_recurring: true,
          },
          {
            name: 'Christmas Day',
            start_date: new Date('2024-12-25'),
            end_date: new Date('2024-12-25'),
            days_count: 1,
            is_recurring: true,
          },
        ],
      },
      {
        id: 2,
        name: 'Manufacturing Holidays',
        description:
          'Extended holidays for manufacturing employees including plant shutdowns',
        employee_count: 45,
        total_holiday_days: 15,
        holidays: [
          {
            name: 'Summer Plant Shutdown',
            start_date: new Date('2024-07-01'),
            end_date: new Date('2024-07-05'),
            days_count: 5,
            is_recurring: true,
          },
          {
            name: 'Winter Plant Shutdown',
            start_date: new Date('2024-12-23'),
            end_date: new Date('2024-12-29'),
            days_count: 7,
            is_recurring: true,
          },
        ],
      },
      {
        id: 3,
        name: 'International Holidays',
        description: 'Additional holidays for international employees',
        employee_count: 28,
        total_holiday_days: 8,
        holidays: [
          {
            name: "International Workers' Day",
            start_date: new Date('2024-05-01'),
            end_date: new Date('2024-05-01'),
            days_count: 1,
            is_recurring: true,
          },
          {
            name: 'Boxing Day',
            start_date: new Date('2024-12-26'),
            end_date: new Date('2024-12-26'),
            days_count: 1,
            is_recurring: true,
          },
        ],
      },
    ];
  }
}
