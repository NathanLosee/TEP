import { Component, inject, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import {
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import { UserService, UserPasswordChange } from '../../services/user.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

export interface PasswordChangeDialogData {
  badgeNumber: string;
  isAdmin: boolean; // If true, don't require current password
}

// Custom validator to check if passwords match
function passwordMatchValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const newPassword = control.get('newPassword');
    const confirmPassword = control.get('confirmPassword');

    if (!newPassword || !confirmPassword) {
      return null;
    }

    return newPassword.value === confirmPassword.value
      ? null
      : { passwordMismatch: true };
  };
}

@Component({
  selector: 'app-password-change-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatDialogModule,
  ],
  templateUrl: './password-change-dialog.component.html',
  styleUrl: './password-change-dialog.component.scss',
})
export class PasswordChangeDialogComponent {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  private errorDialog = inject(ErrorDialogComponent);
  private dialogRef = inject(MatDialogRef<PasswordChangeDialogComponent>);

  passwordForm: FormGroup;
  hideCurrentPassword = true;
  hideNewPassword = true;
  hideConfirmPassword = true;
  isLoading = false;

  constructor(@Inject(MAT_DIALOG_DATA) public data: PasswordChangeDialogData) {
    // If admin changing another user's password, don't require current password
    const validators = data.isAdmin
      ? {}
      : { currentPassword: ['', [Validators.required]] };

    this.passwordForm = this.fb.group(
      {
        ...validators,
        newPassword: ['', [Validators.required, Validators.minLength(8)]],
        confirmPassword: ['', [Validators.required]],
      },
      { validators: passwordMatchValidator() }
    );
  }

  get passwordsMatch(): boolean {
    return !this.passwordForm.hasError('passwordMismatch');
  }

  onSubmit() {
    if (this.passwordForm.invalid) {
      return;
    }

    this.isLoading = true;

    const passwordData: UserPasswordChange = {
      badge_number: this.data.badgeNumber,
      password: this.data.isAdmin ? '' : this.passwordForm.value.currentPassword,
      new_password: this.passwordForm.value.newPassword,
    };

    this.userService
      .updateUserPassword(this.data.badgeNumber, passwordData)
      .subscribe({
        next: () => {
          this.isLoading = false;
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorDialog.openErrorDialog(
            'Failed to change password',
            error
          );
        },
      });
  }

  onCancel() {
    this.dialogRef.close(false);
  }
}
