import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import {
  AuthRole,
  AuthRoleService,
  Permission,
} from '../../../services/auth-role.service';

export interface AuthRoleFormDialogData {
  editAuthRole?: AuthRole | null;
}

@Component({
  selector: 'app-auth-role-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatChipsModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './auth-role-form-dialog.component.html',
  styleUrl: './auth-role-form-dialog.component.scss',
})
export class AuthRoleFormDialogComponent {
  private fb = inject(FormBuilder);
  private authRoleService = inject(AuthRoleService);
  private dialogRef = inject(MatDialogRef<AuthRoleFormDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as AuthRoleFormDialogData;

  authRoleForm!: FormGroup;
  isLoading = false;
  isEditMode = false;

  // Permissions
  availablePermissions: { [category: string]: Permission[] } = {};
  selectedPermissions: Set<string> = new Set();

  // Make Object available in template
  Object = Object;

  constructor() {
    this.isEditMode = !!this.data.editAuthRole;
    this.initializeForm();
    this.loadPermissions();
  }

  private initializeForm() {
    this.authRoleForm = this.fb.group({
      name: [this.data.editAuthRole?.name || '', [Validators.required]],
    });

    // Pre-populate selected permissions if editing
    if (this.data.editAuthRole?.permissions) {
      this.data.editAuthRole.permissions.forEach((p) => {
        this.selectedPermissions.add(p.resource);
      });
    }
  }

  private loadPermissions() {
    this.availablePermissions = this.authRoleService.getPermissionsByCategory();
  }

  togglePermission(permission: Permission) {
    if (this.selectedPermissions.has(permission.resource)) {
      this.selectedPermissions.delete(permission.resource);
    } else {
      this.selectedPermissions.add(permission.resource);
    }
  }

  isPermissionSelected(permission: Permission): boolean {
    return this.selectedPermissions.has(permission.resource);
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

  getSelectedPermissionsCount(category: string): number {
    return this.availablePermissions[category].filter((p) =>
      this.selectedPermissions.has(p.resource)
    ).length;
  }

  submitForm() {
    if (this.authRoleForm.valid) {
      this.isLoading = true;

      // Build permissions array with full Permission objects (including description)
      const permissions: Permission[] = [];
      for (const category of Object.keys(this.availablePermissions)) {
        for (const perm of this.availablePermissions[category]) {
          if (this.selectedPermissions.has(perm.resource)) {
            permissions.push(perm);
          }
        }
      }

      const authRoleData: AuthRole = {
        name: this.authRoleForm.value.name,
        permissions,
      };

      if (this.isEditMode && this.data.editAuthRole) {
        // Update existing auth role
        this.authRoleService
          .updateAuthRole(this.data.editAuthRole.id!, authRoleData)
          .subscribe({
            next: (updatedRole) => {
              this.dialogRef.close(updatedRole);
              this.isLoading = false;
            },
            error: (error) => {
              this.isLoading = false;
            },
          });
      } else {
        // Create new auth role
        this.authRoleService.createAuthRole(authRoleData).subscribe({
          next: (newRole) => {
            this.dialogRef.close(newRole);
            this.isLoading = false;
          },
          error: (error) => {
            this.isLoading = false;
          },
        });
      }
    }
  }

  cancelForm() {
    this.dialogRef.close();
  }
}
