import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthRole, AuthRoleService } from '../../../services/auth-role.service';
import { User } from '../../../services/user.service';

@Component({
  selector: 'app-auth-role-details-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatChipsModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatDividerModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './auth-role-details-dialog.component.html',
  styleUrl: './auth-role-details-dialog.component.scss',
})
export class AuthRoleDetailsDialogComponent implements OnInit {
  private dialogRef = inject(MatDialogRef<AuthRoleDetailsDialogComponent>);
  private authRoleService = inject(AuthRoleService);
  readonly data = inject<{ authRole: AuthRole }>(MAT_DIALOG_DATA);

  assignedUsers: User[] = [];
  isLoading = true;

  // Group permissions by category
  permissionsByCategory: { [category: string]: string[] } = {};

  ngOnInit() {
    this.loadAssignedUsers();
    this.groupPermissions();
  }

  private loadAssignedUsers() {
    this.authRoleService.getUsersByAuthRole(this.data.authRole.id!).subscribe({
      next: (users) => {
        // Filter out root user (id=0)
        this.assignedUsers = users.filter((user) => user.id !== 0);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load users:', error);
        this.isLoading = false;
      },
    });
  }

  private groupPermissions() {
    this.permissionsByCategory = {};
    this.data.authRole.permissions.forEach((p) => {
      const parts = p.resource.split('.');
      const category = parts[0];
      const action = parts[1] || p.resource;

      if (!this.permissionsByCategory[category]) {
        this.permissionsByCategory[category] = [];
      }
      this.permissionsByCategory[category].push(action);
    });
  }

  getCategoryName(category: string): string {
    const names: { [key: string]: string } = {
      auth_role: 'Auth Roles',
      department: 'Departments',
      employee: 'Employees',
      event_log: 'Event Logs',
      holiday_group: 'Holiday Groups',
      org_unit: 'Organizational Units',
      registered_browser: 'Registered Browsers',
      report: 'Reports',
      timeclock: 'Timeclock',
      user: 'Users',
    };
    return names[category] || category.charAt(0).toUpperCase() + category.slice(1);
  }

  getCategoryIcon(category: string): string {
    const icons: { [key: string]: string } = {
      auth_role: 'security',
      department: 'business',
      employee: 'people',
      event_log: 'history',
      holiday_group: 'event',
      org_unit: 'account_tree',
      registered_browser: 'devices',
      report: 'assessment',
      timeclock: 'schedule',
      user: 'person',
    };
    return icons[category] || 'settings';
  }

  get categoryKeys(): string[] {
    return Object.keys(this.permissionsByCategory);
  }

  editRole() {
    this.dialogRef.close({ action: 'edit', authRole: this.data.authRole });
  }
}
