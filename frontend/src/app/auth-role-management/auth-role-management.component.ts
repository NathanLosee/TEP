import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatTableModule } from "@angular/material/table";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatChipsModule } from "@angular/material/chips";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatDialogModule, MatDialog } from "@angular/material/dialog";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { MatTabsModule } from "@angular/material/tabs";
import { MatExpansionModule } from "@angular/material/expansion";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatDividerModule } from "@angular/material/divider";
import {
  AuthRoleService,
  AuthRole,
  AuthRoleBase,
  Permission,
  UserResponse,
} from "../../services/auth-role.service";
import { UserService, User } from "../../services/user.service";

@Component({
  selector: "app-auth-role-management",
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
    MatCheckboxModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTabsModule,
    MatExpansionModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatDividerModule,
  ],
  templateUrl: "./auth-role-management.component.html",
  styleUrl: "./auth-role-management.component.scss",
})
export class AuthRoleManagementComponent implements OnInit {
  private authRoleService = inject(AuthRoleService);
  private userService = inject(UserService);
  private formBuilder = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);

  // Data
  authRoles: AuthRole[] = [];
  users: User[] = [];
  filteredAuthRoles: AuthRole[] = [];
  selectedRole: AuthRole | null = null;
  selectedRoleUsers: UserResponse[] = [];

  // Forms
  roleForm: FormGroup;

  // UI State
  isLoading = false;
  searchTerm = "";
  showCreateForm = false;
  editingRole: AuthRole | null = null;

  // Permissions
  availablePermissions: { [category: string]: { [key: string]: string } } = {};
  selectedPermissions: Set<string> = new Set();

  // Table columns
  displayedColumns = ["name", "permissions", "users", "actions"];

  constructor() {
    this.roleForm = this.formBuilder.group({
      name: [
        "",
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(50),
        ],
      ],
      permissions: [[]],
    });
  }

  ngOnInit() {
    this.loadAuthRoles();
    this.loadUsers();
    this.availablePermissions = this.authRoleService.getPermissionsByCategory();
  }

  loadAuthRoles() {
    this.isLoading = true;
    this.authRoleService.getAuthRoles().subscribe({
      next: (roles) => {
        this.authRoles = roles;
        this.applySearchFilter();
        this.isLoading = false;
      },
      error: (error) => {
        this.showSnackBar(
          "Failed to load auth roles: " +
            (error.error?.detail || error.message),
          "error",
        );
        this.isLoading = false;
      },
    });
  }

  loadUsers() {
    this.userService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
      },
      error: (error) => {
        this.showSnackBar(
          "Failed to load users: " + (error.error?.detail || error.message),
          "error",
        );
      },
    });
  }

  loadRoleUsers(roleId: number) {
    this.authRoleService.getUsersByAuthRole(roleId).subscribe({
      next: (users) => {
        this.selectedRoleUsers = users;
      },
      error: (error) => {
        this.showSnackBar(
          "Failed to load role users: " +
            (error.error?.detail || error.message),
          "error",
        );
      },
    });
  }

  applySearchFilter() {
    if (!this.searchTerm.trim()) {
      this.filteredAuthRoles = [...this.authRoles];
    } else {
      const term = this.searchTerm.toLowerCase();
      this.filteredAuthRoles = this.authRoles.filter(
        (role) =>
          role.name.toLowerCase().includes(term) ||
          role.permissions.some((p) => p.resource.toLowerCase().includes(term)),
      );
    }
  }

  onSearchChange() {
    this.applySearchFilter();
  }

  showCreateRoleForm() {
    this.showCreateForm = true;
    this.editingRole = null;
    this.selectedPermissions.clear();
    this.roleForm.reset();
    this.roleForm.patchValue({ permissions: [] });
  }

  editRole(role: AuthRole) {
    this.editingRole = role;
    this.showCreateForm = true;
    this.selectedPermissions = new Set(role.permissions.map((p) => p.resource));
    this.roleForm.patchValue({
      name: role.name,
      permissions: role.permissions.map((p) => p.resource),
    });
  }

  cancelForm() {
    this.showCreateForm = false;
    this.editingRole = null;
    this.selectedPermissions.clear();
    this.roleForm.reset();
  }

  togglePermission(resource: string) {
    if (this.selectedPermissions.has(resource)) {
      this.selectedPermissions.delete(resource);
    } else {
      this.selectedPermissions.add(resource);
    }

    // Update form control
    this.roleForm.patchValue({
      permissions: Array.from(this.selectedPermissions),
    });
  }

  isPermissionSelected(resource: string): boolean {
    return this.selectedPermissions.has(resource);
  }

  onSubmit() {
    if (this.roleForm.invalid) {
      this.showSnackBar(
        "Please fill in all required fields correctly",
        "error",
      );
      return;
    }

    const formValue = this.roleForm.value;
    const roleData: AuthRoleBase = {
      name: formValue.name,
      permissions: Array.from(this.selectedPermissions).map((resource) => ({
        resource,
      })),
    };

    this.isLoading = true;

    if (this.editingRole) {
      // Update existing role
      const updateData: AuthRole = {
        ...roleData,
        id: this.editingRole.id,
      };

      this.authRoleService
        .updateAuthRole(this.editingRole.id, updateData)
        .subscribe({
          next: (updatedRole) => {
            this.showSnackBar("Auth role updated successfully", "success");
            this.loadAuthRoles();
            this.cancelForm();
            this.isLoading = false;
          },
          error: (error) => {
            this.showSnackBar(
              "Failed to update auth role: " +
                (error.error?.detail || error.message),
              "error",
            );
            this.isLoading = false;
          },
        });
    } else {
      // Create new role
      this.authRoleService.createAuthRole(roleData).subscribe({
        next: (newRole) => {
          this.showSnackBar("Auth role created successfully", "success");
          this.loadAuthRoles();
          this.cancelForm();
          this.isLoading = false;
        },
        error: (error) => {
          this.showSnackBar(
            "Failed to create auth role: " +
              (error.error?.detail || error.message),
            "error",
          );
          this.isLoading = false;
        },
      });
    }
  }

  deleteRole(role: AuthRole) {
    if (
      confirm(
        `Are you sure you want to delete the auth role "${role.name}"? This action cannot be undone.`,
      )
    ) {
      this.isLoading = true;
      this.authRoleService.deleteAuthRole(role.id).subscribe({
        next: () => {
          this.showSnackBar("Auth role deleted successfully", "success");
          this.loadAuthRoles();
          this.isLoading = false;
        },
        error: (error) => {
          this.showSnackBar(
            "Failed to delete auth role: " +
              (error.error?.detail || error.message),
            "error",
          );
          this.isLoading = false;
        },
      });
    }
  }

  viewRoleDetails(role: AuthRole) {
    this.selectedRole = role;
    this.loadRoleUsers(role.id);
  }

  assignUserToRole(userId: number) {
    if (!this.selectedRole) return;

    this.authRoleService
      .assignUserToRole(this.selectedRole.id, userId)
      .subscribe({
        next: (users) => {
          this.selectedRoleUsers = users;
          this.showSnackBar("User assigned to role successfully", "success");
        },
        error: (error) => {
          this.showSnackBar(
            "Failed to assign user: " + (error.error?.detail || error.message),
            "error",
          );
        },
      });
  }

  removeUserFromRole(userId: number) {
    if (!this.selectedRole) return;

    if (confirm("Are you sure you want to remove this user from the role?")) {
      this.authRoleService
        .removeUserFromRole(this.selectedRole.id, userId)
        .subscribe({
          next: (users) => {
            this.selectedRoleUsers = users;
            this.showSnackBar("User removed from role successfully", "success");
          },
          error: (error) => {
            this.showSnackBar(
              "Failed to remove user: " +
                (error.error?.detail || error.message),
              "error",
            );
          },
        });
    }
  }

  getUnassignedUsers(): User[] {
    const assignedUserIds = new Set(this.selectedRoleUsers.map((u) => u.id));
    return this.users.filter((user) => !assignedUserIds.has(user.id));
  }

  getCategoryName(category: string): string {
    const names: { [key: string]: string } = {
      auth_role: "Auth Roles",
      department: "Departments",
      employee: "Employees",
      event_log: "Event Logs",
      holiday_group: "Holiday Groups",
      org_unit: "Organizational Units",
      timeclock: "Timeclock",
      user: "Users",
    };
    return (
      names[category] || category.charAt(0).toUpperCase() + category.slice(1)
    );
  }

  getCategoryIcon(category: string): string {
    const icons: { [key: string]: string } = {
      auth_role: "security",
      department: "business",
      employee: "people",
      event_log: "history",
      holiday_group: "event",
      org_unit: "account_tree",
      timeclock: "schedule",
      user: "person",
    };
    return icons[category] || "settings";
  }

  getSelectedPermissionsCount(category: string): number {
    const categoryPermissions = Object.keys(
      this.availablePermissions[category] || {},
    );
    return categoryPermissions.filter((p) => this.selectedPermissions.has(p))
      .length;
  }

  // Make Array and Object available in template
  Array = Array;
  Object = Object;

  getPermissionCount(): number {
    return this.authRoles.reduce(
      (total, role) => total + role.permissions.length,
      0,
    );
  }

  getUserCount(): number {
    const userIds = new Set();
    this.authRoles.forEach((role) => {
      // Note: We would need to load users for each role to get accurate count
      // For now, return total unique users
    });
    return this.users.length;
  }

  private showSnackBar(
    message: string,
    type: "success" | "error" | "info" = "info",
  ) {
    this.snackBar.open(message, "Close", {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
