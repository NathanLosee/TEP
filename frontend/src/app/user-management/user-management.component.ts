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
import { MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AuthRoleService } from '../../services/auth-role.service';
import {
  AuthRole,
  User,
  UserBase,
  UserPasswordChange,
  UserService,
} from '../../services/user.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { UserFormDialogComponent } from './user-management-form-dialog/user-form-dialog.component';

interface Employee {
  badge_number: string;
  name: string;
}

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatDividerModule,
    MatSlideToggleModule,
  ],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.scss',
})
export class UserManagementComponent implements OnInit {
  private userService = inject(UserService);
  private authRoleService = inject(AuthRoleService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  // Data
  users: User[] = [];
  authRoles: AuthRole[] = [];
  employees: Employee[] = [];
  filteredUsers: User[] = [];

  // UI State
  isLoading = false;
  searchTerm = '';

  // Table columns
  displayedColumns = ['badge_number', 'roles', 'actions'];

  ngOnInit() {
    this.loadUsers();
    this.loadAuthRoles();
    this.loadEmployees();
  }

  loadUsers() {
    this.isLoading = true;
    this.userService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.applySearchFilter();
        this.isLoading = false;
      },
      error: (error) => {
        this.showSnackBar(
          'Failed to load users: ' + (error.error?.detail || error.message),
          'error'
        );
        this.isLoading = false;
      },
    });
  }

  loadAuthRoles() {
    this.authRoleService.getAuthRoles().subscribe({
      next: (roles) => {
        this.authRoles = roles;
      },
      error: (error) => {
        this.showSnackBar(
          'Failed to load auth roles: ' +
            (error.error?.detail || error.message),
          'error'
        );
      },
    });
  }

  loadEmployees() {
    // Mock employee data - in real app, this would come from employee service
    this.employees = [
      { badge_number: 'ADMIN001', name: 'System Administrator' },
      { badge_number: 'MGR001', name: 'Manager One' },
      { badge_number: 'EMP001', name: 'Employee One' },
      { badge_number: 'EMP002', name: 'Employee Two' },
      { badge_number: 'SUP001', name: 'Supervisor One' },
      { badge_number: 'HR001', name: 'HR Representative' },
      { badge_number: 'IT001', name: 'IT Support' },
      { badge_number: 'FIN001', name: 'Finance Manager' },
      { badge_number: 'OP001', name: 'Operations Lead' },
      { badge_number: 'QA001', name: 'Quality Assurance' },
    ];
  }

  onSearchChange() {
    this.applySearchFilter();
  }

  filterUsers() {
    this.applySearchFilter();
  }

  applySearchFilter() {
    if (!this.searchTerm.trim()) {
      this.filteredUsers = [...this.users];
    } else {
      const term = this.searchTerm.toLowerCase();
      this.filteredUsers = this.users.filter((user) =>
        user.badge_number.toLowerCase().includes(term)
      );
    }
  }

  createUser() {
    const dialogRef = this.dialog.open(UserFormDialogComponent, {
      width: '600px',
      data: {
        authRoles: this.authRoles,
        employees: this.employees,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.users.push(result);
        this.filterUsers();
        this.showSnackBar('User account created successfully', 'success');
      }
    });
  }

  editUser(user: User) {
    const dialogRef = this.dialog.open(UserFormDialogComponent, {
      width: '600px',
      data: {
        editUser: user,
        authRoles: this.authRoles,
        employees: this.employees,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const index = this.users.findIndex((u) => u.id === user.id);
        if (index > -1) {
          this.users[index] = result;
          this.filterUsers();
          this.showSnackBar('User updated successfully', 'success');
        }
      }
    });
  }

  deleteUser(user: User) {
    if (
      confirm(
        `Are you sure you want to delete the user account for "${user.badge_number}"? This action cannot be undone.`
      )
    ) {
      this.isLoading = true;
      this.userService.deleteUser(user.id!).subscribe({
        next: () => {
          this.showSnackBar('User account deleted successfully', 'success');
          this.loadUsers();
          this.isLoading = false;
        },
        error: (error) => {
          this.showSnackBar(
            'Failed to delete user: ' + (error.error?.detail || error.message),
            'error'
          );
          this.isLoading = false;
        },
      });
    }
  }

  getEmployeeName(badgeNumber: string): string {
    const employee = this.employees.find(
      (emp) => emp.badge_number === badgeNumber
    );
    return employee ? employee.name : 'Unknown Employee';
  }

  getUserRoleNames(user: User): string[] {
    // This would need to be populated from the backend or cached
    // For now, return empty array as roles are loaded separately
    return [];
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
