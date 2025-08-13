import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule, NgForm, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../../services/user.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatCardModule,
    MatProgressSpinnerModule,
    ReactiveFormsModule,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private userService = inject(UserService);
  private router = inject(Router);
  readonly errorDialog = inject(ErrorDialogComponent);

  hidePassword = true;
  isLoading = false;

  constructor() {}

  /**
   * Handle the form submission
   * @param loginData The form data
   */
  onSubmit(loginData: NgForm) {
    if (loginData.invalid) {
      return;
    }

    this.isLoading = true;

    const badgeNumber = loginData.form.value.badgeNumber;
    const password = loginData.form.value.password;

    const formData = new FormData();
    formData.append('username', badgeNumber);
    formData.append('password', password);

    this.userService.login(formData).subscribe({
      next: (response) => {
        console.log('Login successful:', response);
        localStorage.setItem('access_token', response.access_token);
        this.isLoading = false;
        this.router.navigate(['/admin']);
      },
      error: (error) => {
        console.error('Login failed:', error);
        this.isLoading = false;
        this.errorDialog.openErrorDialog(
          'Login failed. Please check your credentials.'
        );
      },
    });
  }
}
