import { Component, inject } from '@angular/core';
import { FormsModule, NgForm, ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router } from '@angular/router';
import { UserService } from '../../services/user.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    ReactiveFormsModule,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private userService = inject(UserService);
  private router = inject(Router);
  readonly errorDialog = inject(ErrorDialogComponent);

  constructor() {}

  /**
   * Handle the form submission
   * @param loginData The form data
   */
  onSubmit(loginData: NgForm) {
    if (loginData.invalid) {
      return;
    }
    const formData = new FormData();
    formData.append('username', loginData.form.value.badgeNumber);
    formData.append('password', loginData.form.value.password);

    this.userService.login(formData).subscribe({
      next: (response) => {
        console.log('Login successful:', response);
        localStorage.setItem('access_token', response.access_token);
        this.router.navigate(['/admin']);
      },
      error: (error) => {
        console.error('Login failed:', error);
        this.errorDialog.openErrorDialog(
          'Login failed. Please check your credentials.'
        );
      },
    });
  }
}
