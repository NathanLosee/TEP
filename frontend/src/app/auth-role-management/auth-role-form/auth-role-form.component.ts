import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  AuthRole,
  AuthRoleService,
  Permission,
} from '../../../services/auth-role.service';

@Component({
  selector: 'app-auth-role-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatCardModule,
    MatCheckboxModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatTabsModule,
  ],
  templateUrl: './auth-role-form.component.html',
})
export class AuthRoleFormComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private authRoleService = inject(AuthRoleService);

  // Make Array and Object available in template
  Array = Array;
  Object = Object;

  authRoleForm: FormGroup;
  isLoading = false;

  // Permissions
  availablePermissions: { [category: string]: Permission[] } = {};
  selectedPermissions: Set<Permission> = new Set();

  @Output() formSubmitted = new EventEmitter<AuthRole>();
  @Output() formCancelled = new EventEmitter<void>();

  constructor() {
    this.authRoleForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      holidays: this.formBuilder.array([]),
    });
  }

  ngOnInit() {
    this.availablePermissions = this.authRoleService.getPermissionsByCategory();
  }

  getPermissions(): Permission[] {
    return Array.from(this.selectedPermissions);
  }

  togglePermission(resource: Permission) {
    if (this.selectedPermissions.has(resource)) {
      this.selectedPermissions.delete(resource);
    } else {
      this.selectedPermissions.add(resource);
    }

    // Update form control
    this.authRoleForm.patchValue({
      permissions: Array.from(this.selectedPermissions),
    });
  }

  isPermissionSelected(resource: Permission): boolean {
    return this.selectedPermissions.has(resource);
  }

  getCategoryName(category: string): string {
    const names: { [key: string]: string } = {
      auth_role: 'Auth Roles',
      department: 'Departments',
      employee: 'Employees',
      event_log: 'Event Logs',
      holiday_group: 'Holiday Groups',
      org_unit: 'Organizational Units',
      timeclock: 'Timeclock',
      user: 'Users',
    };
    return (
      names[category] || category.charAt(0).toUpperCase() + category.slice(1)
    );
  }

  getCategoryIcon(category: string): string {
    const icons: { [key: string]: string } = {
      auth_role: 'security',
      department: 'business',
      employee: 'people',
      event_log: 'history',
      holiday_group: 'event',
      org_unit: 'account_tree',
      timeclock: 'schedule',
      user: 'person',
    };
    return icons[category] || 'settings';
  }

  getSelectedPermissionsCount(category: string): number {
    return this.availablePermissions[category].filter((p) =>
      this.selectedPermissions.has(p)
    ).length;
  }

  getFormData(): AuthRole {
    return {
      name: this.authRoleForm.get('name')?.value,
      permissions: this.getPermissions(),
    };
  }

  patchForm(authRole: AuthRole): void {
    this.authRoleForm.patchValue({
      name: authRole.name,
      permissions: authRole.permissions,
    });
  }

  submitForm() {
    if (this.authRoleForm.valid) {
      this.formSubmitted.emit(this.getFormData());
    }
  }

  cancelForm() {
    this.formCancelled.emit();
  }

  resetForm(): void {
    this.authRoleForm.reset();
    this.selectedPermissions.clear();
  }
}
