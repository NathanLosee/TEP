import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
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
import { AuthRoleService } from '../../services/auth-role.service';
import {
  AuthRole,
  User,
  UserService,
} from '../../services/user.service';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';
import { extractErrorDetail } from '../error-dialog/error-dialog.component';
import { PasswordChangeDialogComponent } from '../password-change-dialog/password-change-dialog.component';
import { PermissionService } from '../../services/permission.service';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../shared/models/table.models';
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
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatChipsModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTabsModule,
    MatTooltipModule,
    DisableIfNoPermissionDirective,
    GenericTableComponent,
    TableCellDirective,
  ],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.scss',
})
export class UserManagementComponent implements OnInit {
  private userService = inject(UserService);
  private authRoleService = inject(AuthRoleService);
  private permissionService = inject(PermissionService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  // Data
  users: User[] = [];
  authRoles: AuthRole[] = [];
  employees: Employee[] = [];
  filteredUsers: User[] = [];
  userRolesMap: Map<number, AuthRole[]> = new Map();

  // UI State
  isLoading = false;
  searchTerm = '';

  // Table configuration
  columns: TableColumn<User>[] = [
    {
      key: 'badge_number',
      header: 'User / Employee',
      type: 'template',
    },
    {
      key: 'roles',
      header: 'Auth Roles',
      type: 'template',
    },
  ];

  actions: TableAction<User>[] = [
    {
      icon: 'edit',
      tooltip: 'Edit User',
      action: 'edit',
      permission: 'user.update',
    },
    {
      icon: 'lock',
      tooltip: 'Change Password',
      action: 'changePassword',
      permission: 'user.update',
    },
    {
      icon: 'delete',
      tooltip: 'Delete User',
      action: 'delete',
      color: 'warn',
      permission: 'user.delete',
    },
  ];

  ngOnInit() {
    this.loadUsers();
    this.loadAuthRoles();
    this.loadEmployees();
  }

  loadUsers() {
    this.isLoading = true;
    this.userService.getUsers().subscribe({
      next: (users) => {
        // Filter out root user (id=0)
        this.users = users.filter(user => user.id !== 0);
        this.loadUserRoles();
        this.applySearchFilter();
        this.isLoading = false;
      },
      error: (error) => {
        this.showSnackBar(
          'Failed to load users: ' + extractErrorDetail(error),
          'error'
        );
        this.isLoading = false;
      },
    });
  }

  loadUserRoles() {
    // Load auth roles for each user
    this.users.forEach((user) => {
      if (user.id) {
        this.userService.getUserAuthRoles(user.id).subscribe({
          next: (roles) => {
            // Filter out root role (id=0)
            const filteredRoles = roles.filter(role => role.id !== 0);
            this.userRolesMap.set(user.id!, filteredRoles);
          },
          error: (error) => {
            console.error(`Failed to load roles for user ${user.badge_number}`, error);
          },
        });
      }
    });
  }

  loadAuthRoles() {
    this.authRoleService.getAuthRoles().subscribe({
      next: (roles) => {
        // Filter out root role (id=0 or name='root')
        this.authRoles = roles.filter(role => role.id !== 0 && role.name.toLowerCase() !== 'root');
      },
      error: (error) => {
        this.showSnackBar(
          'Failed to load auth roles: ' +
            extractErrorDetail(error),
          'error'
        );
      },
    });
  }

  loadEmployees() {
    // Mock employee data - in real app, this would come from employee service
    // Badge numbers are 6-digit strings
    this.employees = [
      { badge_number: '100001', name: 'John Doe' },
      { badge_number: '100002', name: 'Jane Smith' },
      { badge_number: '100003', name: 'Bob Johnson' },
      { badge_number: '100004', name: 'Alice Williams' },
      { badge_number: '100005', name: 'Charlie Brown' },
      { badge_number: '100006', name: 'Diana Davis' },
      { badge_number: '100007', name: 'Eve Miller' },
      { badge_number: '100008', name: 'Frank Wilson' },
      { badge_number: '100009', name: 'Grace Moore' },
      { badge_number: '100010', name: 'Henry Taylor' },
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

  onTableAction(event: TableActionEvent<User>) {
    switch (event.action) {
      case 'edit':
        this.editUser(event.row);
        break;
      case 'changePassword':
        this.changeUserPassword(event.row);
        break;
      case 'delete':
        this.deleteUser(event.row);
        break;
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

    dialogRef.afterClosed().subscribe((result: any) => {
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

    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.loadUsers();
        this.showSnackBar('User account updated successfully', 'success');
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
            'Failed to delete user: ' + extractErrorDetail(error),
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

  getUserRoles(user: User): AuthRole[] {
    if (!user.id) return [];
    return this.userRolesMap.get(user.id) || [];
  }

  changeUserPassword(user: User) {
    // Check if user has admin permission
    const hasAdminPermission = this.permissionService.hasPermission('user.update');

    const dialogRef = this.dialog.open(PasswordChangeDialogComponent, {
      width: '500px',
      data: {
        badgeNumber: user.badge_number,
        isAdmin: hasAdminPermission,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.showSnackBar(
          `Password changed successfully for ${user.badge_number}`,
          'success'
        );
      }
    });
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
