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
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { User, UserService } from '../../../services/user.service';
import { Employee, EmployeeService } from '../../../services/employee.service';
import { AuthRole, AuthRoleService } from '../../../services/auth-role.service';

export interface UserFormDialogData {
  editUser?: User | null;
  employees?: Employee[];
  authRoles?: AuthRole[];
}

@Component({
  selector: 'app-user-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatSelectModule,
    MatCheckboxModule,
  ],
  templateUrl: './user-form-dialog.component.html',
  styleUrl: './user-form-dialog.component.scss',
})
export class UserFormDialogComponent {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  private employeeService = inject(EmployeeService);
  private authRoleService = inject(AuthRoleService);
  private dialogRef = inject(MatDialogRef<UserFormDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as UserFormDialogData;

  userForm!: FormGroup;
  isLoading = false;
  isEditMode = false;

  employees: Employee[] = [];
  authRoles: AuthRole[] = [];

  constructor() {
    this.isEditMode = !!this.data.editUser;
    this.initializeForm();
    this.loadFormData();
  }

  private initializeForm() {
    this.userForm = this.fb.group({
      badge_number: [
        this.data.editUser?.badge_number || '',
        [Validators.required],
      ],
      password: [
        '',
        this.isEditMode ? [] : [Validators.required, Validators.minLength(6)],
      ],
      confirmPassword: [''],
      is_active: [
        this.data.editUser?.is_active !== undefined ? this.data.editUser.is_active : true,
      ],
      auth_role_ids: [
        this.data.editUser?.auth_roles?.map(role => role.id) || [],
      ],
    });

    // Add password confirmation validator
    this.userForm.get('confirmPassword')?.setValidators([
      this.passwordMatchValidator.bind(this)
    ]);
  }

  private passwordMatchValidator(control: any) {
    const password = this.userForm?.get('password')?.value;
    const confirmPassword = control.value;
    
    if (password && confirmPassword && password !== confirmPassword) {
      return { passwordMismatch: true };
    }
    return null;
  }

  private loadFormData() {
    this.employees = this.data.employees || [];
    this.authRoles = this.data.authRoles || [];
  }

  submitForm() {
    if (this.userForm.valid) {
      this.isLoading = true;

      const userData = {
        badge_number: this.userForm.value.badge_number,
        password: this.userForm.value.password,
        is_active: this.userForm.value.is_active,
        auth_role_ids: this.userForm.value.auth_role_ids,
      };

      if (this.isEditMode && this.data.editUser) {
        this.userService
          .updateUser(this.data.editUser.id!, userData)
          .subscribe({
            next: (updatedUser) => {
              this.dialogRef.close(updatedUser);
              this.isLoading = false;
            },
            error: (error) => {
              console.error('Error updating user:', error);
              this.isLoading = false;
            },
          });
      } else {
        this.userService.createUser(userData).subscribe({
          next: (newUser) => {
            this.dialogRef.close(newUser);
            this.isLoading = false;
          },
          error: (error) => {
            console.error('Error creating user:', error);
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