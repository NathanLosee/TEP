import { Component, inject } from '@angular/core';
import { FormsModule, NgForm, ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router } from '@angular/router';
import { UserService } from '../../services/user.service';

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

  constructor() {}

  onSubmit(loginData: NgForm) {
    if (loginData.invalid) {
      return;
    }
    const formData = new FormData();
    formData.append('username', loginData.form.value.username);
    formData.append('password', loginData.form.value.password);

    this.userService.login(formData).subscribe((response) => {
      console.log('Login successful:', response);
      this.router.navigate(['/admin']);
    });
  }
}
