import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
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
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AuthRole, AuthRoleService } from '../../services/auth-role.service';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';
import { ErrorDialogComponent, extractErrorDetail } from '../error-dialog/error-dialog.component';
import {
  GenericTableComponent,
  TableCellDirective,
} from '../shared/components/generic-table';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../shared/models/table.models';
import { AuthRoleFormDialogComponent } from './auth-role-form-dialog/auth-role-form-dialog.component';
import { AuthRoleDetailsDialogComponent } from './auth-role-details-dialog/auth-role-details-dialog.component';

@Component({
  selector: 'app-auth-role-management',
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
  templateUrl: './auth-role-management.component.html',
  styleUrl: './auth-role-management.component.scss',
})
export class AuthRoleManagementComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private formBuilder = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private authRoleService = inject(AuthRoleService);

  // Data
  authRoles: AuthRole[] = [];
  filteredRoles: AuthRole[] = [];

  // Forms
  searchForm: FormGroup;

  // UI State
  isLoading = false;

  // Table configuration
  columns: TableColumn<AuthRole>[] = [
    {
      key: 'name',
      header: 'Role Name',
      type: 'icon-text',
      icon: 'security',
    },
    {
      key: 'permissions',
      header: 'Permissions',
      type: 'template',
    },
  ];

  actions: TableAction<AuthRole>[] = [
    {
      icon: 'info',
      tooltip: 'View Details',
      action: 'view',
      permission: 'auth_role.read',
    },
    {
      icon: 'edit',
      tooltip: 'Edit Role',
      action: 'edit',
      color: 'primary',
      permission: 'auth_role.update',
    },
    {
      icon: 'delete',
      tooltip: 'Delete Role',
      action: 'delete',
      color: 'warn',
      permission: 'auth_role.delete',
      disabled: (role: AuthRole) => (role.user_count || 0) > 0,
    },
  ];

  constructor() {
    this.searchForm = this.formBuilder.group({
      name: [''],
    });
  }

  ngOnInit() {
    this.loadAuthRoles();
    this.setupSearchForm();
  }

  loadAuthRoles() {
    this.isLoading = true;
    this.authRoleService.getAuthRoles().subscribe({
      next: (roles) => {
        // Filter out root role (id=0)
        this.authRoles = roles.filter((role) => role.id !== 0);
        this.filterRoles();
        this.isLoading = false;
      },
      error: (error) => {
        this.handleError('Failed to load auth roles', error);
        this.isLoading = false;
      },
    });
  }

  setupSearchForm() {
    this.searchForm.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.filterRoles();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
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

  onTableAction(event: TableActionEvent<AuthRole>) {
    switch (event.action) {
      case 'view':
        this.viewDetails(event.row);
        break;
      case 'edit':
        this.editRole(event.row);
        break;
      case 'delete':
        this.deleteRole(event.row);
        break;
    }
  }

  addAuthRole() {
    const dialogRef = this.dialog.open(AuthRoleFormDialogComponent, {
      width: '700px',
      maxHeight: '90vh',
      data: {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.authRoles.push(result);
        this.filterRoles();
        this.showSnackBar(
          `Auth role "${result.name}" created successfully`,
          'success'
        );
      }
    });
  }

  viewDetails(role: AuthRole) {
    const dialogRef = this.dialog.open(AuthRoleDetailsDialogComponent, {
      width: '600px',
      data: { authRole: role },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'edit') {
        this.editRole(result.authRole);
      }
    });
  }

  editRole(role: AuthRole) {
    const dialogRef = this.dialog.open(AuthRoleFormDialogComponent, {
      width: '700px',
      maxHeight: '90vh',
      data: { editAuthRole: role },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const index = this.authRoles.findIndex((r) => r.id === role.id);
        if (index > -1) {
          this.authRoles[index] = result;
          this.filterRoles();
          this.showSnackBar('Auth role updated successfully', 'success');
        }
      }
    });
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
          this.handleError('Failed to delete auth role', error);
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
    this.dialog.open(ErrorDialogComponent, {
      data: {
        title: 'Error',
        message: `${message}. Please try again.`,
        error: extractErrorDetail(error),
      },
    });
  }
}
