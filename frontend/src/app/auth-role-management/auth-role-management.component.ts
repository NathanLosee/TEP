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
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PartialObserver } from 'rxjs';
import { AuthRole, AuthRoleService } from '../../services/auth-role.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { AuthRoleFormComponent } from './auth-role-form/auth-role-form.component';

@Component({
  selector: 'app-auth-role-management',
  standalone: true,
  imports: [
    AuthRoleFormComponent,
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatDialogModule,
    MatDividerModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSnackBarModule,
    MatTableModule,
    MatTabsModule,
    MatTooltipModule,
    ReactiveFormsModule,
  ],
  templateUrl: './auth-role-management.component.html',
  styleUrl: './auth-role-management.component.scss',
})
export class AuthRoleManagementComponent implements OnInit {
  private formBuilder = inject(FormBuilder);
  private errorDialog = inject(ErrorDialogComponent);
  private snackBar = inject(MatSnackBar);

  private authRoleService = inject(AuthRoleService);
  private authRoleFormComponent = new AuthRoleFormComponent();

  // Data
  authRoles: AuthRole[] = [];
  filteredRoles: AuthRole[] = [];
  selectedRole: AuthRole | null = null;

  // Forms
  searchForm: FormGroup;
  roleForm: FormGroup;

  // UI State
  isLoading = false;
  showForm = false;
  showUsersList = false;

  // Table columns
  displayedColumns = ['name', 'permissions', 'actions'];

  constructor() {
    this.searchForm = this.formBuilder.group({
      name: [''],
    });
    this.roleForm = this.authRoleFormComponent.authRoleForm;
  }

  ngOnInit() {
    this.loadAuthRoles();
    this.setupSearchForm();
  }

  loadAuthRoles() {
    this.isLoading = true;
    this.authRoleService.getAuthRoles().subscribe({
      next: (roles) => {
        this.authRoles = roles;
        this.filterRoles();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to load auth roles: ', error);
        this.isLoading = false;
      },
    });
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterRoles();
    });
  }

  viewUsers(role: AuthRole) {
    this.selectedRole = role;
    this.showUsersList = true;
    this.showForm = false;

    this.authRoleService.getUsersByAuthRole(role.id!).subscribe({
      next: (users) => {
        this.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog(
          'Failed to load users for auth role',
          error
        );
        this.isLoading = false;
      },
    });
  }

  filterRoles() {
    const searchTerm =
      this.searchForm.get('name')?.value?.toLowerCase().trim() || '';

    if (!searchTerm) {
      this.filteredRoles = [...this.authRoles];
      return;
    }
    this.filteredRoles = this.authRoles.filter((role) =>
      role.name.toLowerCase().includes(searchTerm)
    );
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.authRoleFormComponent.resetForm();
    }
  }

  editRole(role: AuthRole) {
    this.selectedRole = role;
    this.showForm = true;
    this.showUsersList = false;
    this.roleForm.patchValue(role);
  }

  cancelAction() {
    this.showForm = false;
    this.showUsersList = false;
    this.selectedRole = null;
  }

  saveAuthRole(authRole: AuthRole) {
    this.authRoleFormComponent.isLoading = true;
    const observer: PartialObserver<AuthRole> = {
      next: (updatedRole) => {
        if (this.selectedRole) {
          // Replace existing role
          const index = this.authRoles.findIndex(
            (r) => r.id === this.selectedRole!.id
          );
          if (index > -1) {
            this.authRoles[index] = updatedRole;
          }
        } else {
          // Add new role
          this.authRoles.push(updatedRole);
        }
        this.filterRoles();
        this.showSnackBar('Auth role saved successfully', 'success');
        this.authRoleFormComponent.resetForm();
        this.cancelAction();
        this.authRoleFormComponent.isLoading = false;
      },
      error: (error) => {
        this.errorDialog.openErrorDialog('Failed to update auth role', error);
        this.authRoleFormComponent.isLoading = false;
      },
    };

    if (this.selectedRole) {
      // Update existing role
      this.authRoleService
        .updateAuthRole(this.selectedRole.id!, authRole)
        .subscribe(observer);
    } else {
      // Create new role
      this.authRoleService.createAuthRole(authRole).subscribe(observer);
    }
  }

  deleteRole(role: AuthRole) {
    if (
      confirm(
        `Are you sure you want to delete "${role.name}"? This action cannot be undone.`
      )
    ) {
      this.isLoading = true;
      this.authRoleService.deleteAuthRole(role.id!).subscribe({
        next: () => {
          const index = this.authRoles.findIndex((r) => r.id === role.id);
          if (index > -1) {
            this.authRoles.splice(index, 1);
            this.filterRoles();
            this.showSnackBar(
              `${role.name} has been deleted successfully`,
              'success'
            );
          }
          this.isLoading = false;
        },
        error: (error) => {
          this.errorDialog.openErrorDialog('Failed to delete auth role', error);
          this.isLoading = false;
        },
      });
    }
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

  getPermissionCount(): number {
    return this.authRoles.reduce(
      (total, role) => total + role.permissions.length,
      0
    );
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
