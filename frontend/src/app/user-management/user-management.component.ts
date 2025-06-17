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
import { MatDialogModule } from "@angular/material/dialog";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { MatTabsModule } from "@angular/material/tabs";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatDividerModule } from "@angular/material/divider";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import {
  UserService,
  User,
  UserBase,
  UserPasswordChange,
  AuthRole,
} from "../../services/user.service";
import { AuthRoleService } from "../../services/auth-role.service";

interface Employee {
  badge_number: string;
  name: string;
}

@Component({
  selector: "app-user-management",
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
  templateUrl: "./user-management.component.html",
  styleUrl: "./user-management.component.scss",
})
export class UserManagementComponent implements OnInit {
  private userService = inject(UserService);
  private authRoleService = inject(AuthRoleService);
  private formBuilder = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);

  // Data
  users: User[] = [];
  authRoles: AuthRole[] = [];
  employees: Employee[] = [];
  filteredUsers: User[] = [];
  selectedUser: User | null = null;
  selectedUserRoles: AuthRole[] = [];

  // Forms
  userForm: FormGroup;
  passwordForm: FormGroup;

  // UI State
  isLoading = false;
  searchTerm = "";
  showCreateForm = false;
  showPasswordForm = false;
  editingUser: User | null = null;

  // Table columns
  displayedColumns = ["badge_number", "roles", "actions"];

  constructor() {
    this.userForm = this.formBuilder.group({
      badge_number: ["", [Validators.required, Validators.minLength(1)]],
      password: ["", [Validators.required, Validators.minLength(6)]],
    });

    this.passwordForm = this.formBuilder.group(
      {
        current_password: ["", [Validators.required]],
        new_password: ["", [Validators.required, Validators.minLength(6)]],
        confirm_password: ["", [Validators.required]],
      },
      { validators: this.passwordMatchValidator },
    );
  }

  ngOnInit() {
    this.loadUsers();
    this.loadAuthRoles();
    this.loadEmployees();
  }

  passwordMatchValidator(group: FormGroup) {
    const newPassword = group.get("new_password")?.value;
    const confirmPassword = group.get("confirm_password")?.value;
    return newPassword === confirmPassword ? null : { passwordMismatch: true };
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
          "Failed to load users: " + (error.error?.detail || error.message),
          "error",
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
          "Failed to load auth roles: " +
            (error.error?.detail || error.message),
          "error",
        );
      },
    });
  }

  loadEmployees() {
    // Mock employee data - in real app, this would come from employee service
    this.employees = [
      { badge_number: "ADMIN001", name: "System Administrator" },
      { badge_number: "MGR001", name: "Manager One" },
      { badge_number: "EMP001", name: "Employee One" },
      { badge_number: "EMP002", name: "Employee Two" },
      { badge_number: "SUP001", name: "Supervisor One" },
      { badge_number: "HR001", name: "HR Representative" },
      { badge_number: "IT001", name: "IT Support" },
      { badge_number: "FIN001", name: "Finance Manager" },
      { badge_number: "OP001", name: "Operations Lead" },
      { badge_number: "QA001", name: "Quality Assurance" },
    ];
  }

  loadUserRoles(userId: number) {
    this.userService.getUserAuthRoles(userId).subscribe({
      next: (roles) => {
        this.selectedUserRoles = roles;
      },
      error: (error) => {
        this.showSnackBar(
          "Failed to load user roles: " +
            (error.error?.detail || error.message),
          "error",
        );
      },
    });
  }

  applySearchFilter() {
    if (!this.searchTerm.trim()) {
      this.filteredUsers = [...this.users];
    } else {
      const term = this.searchTerm.toLowerCase();
      this.filteredUsers = this.users.filter((user) =>
        user.badge_number.toLowerCase().includes(term),
      );
    }
  }

  onSearchChange() {
    this.applySearchFilter();
  }

  showCreateUserForm() {
    this.showCreateForm = true;
    this.editingUser = null;
    this.userForm.reset();
  }

  cancelForm() {
    this.showCreateForm = false;
    this.showPasswordForm = false;
    this.editingUser = null;
    this.userForm.reset();
    this.passwordForm.reset();
  }

  onSubmit() {
    if (this.userForm.invalid) {
      this.showSnackBar(
        "Please fill in all required fields correctly",
        "error",
      );
      return;
    }

    const formValue = this.userForm.value;
    const userData: UserBase = {
      badge_number: formValue.badge_number,
      password: formValue.password,
    };

    this.isLoading = true;

    this.userService.createUser(userData).subscribe({
      next: (newUser) => {
        this.showSnackBar("User account created successfully", "success");
        this.loadUsers();
        this.cancelForm();
        this.isLoading = false;
      },
      error: (error) => {
        this.showSnackBar(
          "Failed to create user: " + (error.error?.detail || error.message),
          "error",
        );
        this.isLoading = false;
      },
    });
  }

  showChangePasswordForm(user: User) {
    this.selectedUser = user;
    this.showPasswordForm = true;
    this.passwordForm.reset();
  }

  onPasswordSubmit() {
    if (this.passwordForm.invalid || !this.selectedUser) {
      this.showSnackBar(
        "Please fill in all required fields correctly",
        "error",
      );
      return;
    }

    if (this.passwordForm.hasError("passwordMismatch")) {
      this.showSnackBar("New passwords do not match", "error");
      return;
    }

    const formValue = this.passwordForm.value;
    const passwordData: UserPasswordChange = {
      badge_number: this.selectedUser.badge_number,
      password: formValue.current_password,
      new_password: formValue.new_password,
    };

    this.isLoading = true;

    this.userService
      .updateUserPassword(this.selectedUser.badge_number, passwordData)
      .subscribe({
        next: (updatedUser) => {
          this.showSnackBar("Password updated successfully", "success");
          this.cancelForm();
          this.isLoading = false;
        },
        error: (error) => {
          this.showSnackBar(
            "Failed to update password: " +
              (error.error?.detail || error.message),
            "error",
          );
          this.isLoading = false;
        },
      });
  }

  deleteUser(user: User) {
    if (
      confirm(
        `Are you sure you want to delete the user account for "${user.badge_number}"? This action cannot be undone.`,
      )
    ) {
      this.isLoading = true;
      this.userService.deleteUser(user.id).subscribe({
        next: () => {
          this.showSnackBar("User account deleted successfully", "success");
          this.loadUsers();
          this.isLoading = false;
        },
        error: (error) => {
          this.showSnackBar(
            "Failed to delete user: " + (error.error?.detail || error.message),
            "error",
          );
          this.isLoading = false;
        },
      });
    }
  }

  viewUserDetails(user: User) {
    this.selectedUser = user;
    this.loadUserRoles(user.id);
  }

  assignRoleToUser(roleId: number) {
    if (!this.selectedUser) return;

    this.authRoleService
      .assignUserToRole(roleId, this.selectedUser.id)
      .subscribe({
        next: () => {
          this.showSnackBar("Role assigned successfully", "success");
          this.loadUserRoles(this.selectedUser!.id);
        },
        error: (error) => {
          this.showSnackBar(
            "Failed to assign role: " + (error.error?.detail || error.message),
            "error",
          );
        },
      });
  }

  removeRoleFromUser(roleId: number) {
    if (!this.selectedUser) return;

    if (confirm("Are you sure you want to remove this role from the user?")) {
      this.authRoleService
        .removeUserFromRole(roleId, this.selectedUser.id)
        .subscribe({
          next: () => {
            this.showSnackBar("Role removed successfully", "success");
            this.loadUserRoles(this.selectedUser!.id);
          },
          error: (error) => {
            this.showSnackBar(
              "Failed to remove role: " +
                (error.error?.detail || error.message),
              "error",
            );
          },
        });
    }
  }

  getUnassignedRoles(): AuthRole[] {
    const assignedRoleIds = new Set(this.selectedUserRoles.map((r) => r.id));
    return this.authRoles.filter((role) => !assignedRoleIds.has(role.id));
  }

  getEmployeeName(badgeNumber: string): string {
    const employee = this.employees.find(
      (emp) => emp.badge_number === badgeNumber,
    );
    return employee ? employee.name : "Unknown Employee";
  }

  getUserRoleNames(user: User): string[] {
    // This would need to be populated from the backend or cached
    // For now, return empty array as roles are loaded separately
    return [];
  }

  getTotalPermissions(): number {
    return this.authRoles.reduce(
      (total, role) => total + role.permissions.length,
      0,
    );
  }

  getActiveUsersCount(): number {
    // In a real app, this would check last login or active status
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
