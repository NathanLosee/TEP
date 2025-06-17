import { Component, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, NgForm, ReactiveFormsModule } from "@angular/forms";
import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { MatInputModule } from "@angular/material/input";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatCardModule } from "@angular/material/card";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { Router, RouterModule } from "@angular/router";
import { UserService } from "../../services/user.service";
import { ErrorDialogComponent } from "../error-dialog/error-dialog.component";

@Component({
  selector: "app-login",
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
  templateUrl: "./login.component.html",
  styleUrl: "./login.component.scss",
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

    // Demo credentials for testing UI
    const badgeNumber = loginData.form.value.badgeNumber;
    const password = loginData.form.value.password;

    // Check for demo credentials first
    if (this.isDemoCredentials(badgeNumber, password)) {
      this.handleDemoLogin();
      return;
    }

    // Regular backend authentication
    const formData = new FormData();
    formData.append("username", badgeNumber);
    formData.append("password", password);

    this.userService.login(formData).subscribe({
      next: (response) => {
        console.log("Login successful:", response);
        localStorage.setItem("access_token", response.access_token);
        this.isLoading = false;
        this.router.navigate(["/admin"]);
      },
      error: (error) => {
        console.error("Login failed:", error);
        this.isLoading = false;
        this.errorDialog.openErrorDialog(
          "Login failed. Please check your credentials.",
        );
      },
    });
  }

  /**
   * Check if the provided credentials are demo credentials
   */
  private isDemoCredentials(badgeNumber: string, password: string): boolean {
    const demoCredentials = [
      { badge: "ADMIN001", password: "demo123" },
      { badge: "DEMO", password: "demo" },
      { badge: "TEST", password: "test" },
      { badge: "admin", password: "admin" },
    ];

    return demoCredentials.some(
      (cred) =>
        cred.badge.toLowerCase() === badgeNumber.toLowerCase() &&
        cred.password === password,
    );
  }

  /**
   * Handle demo login for testing purposes
   */
  private handleDemoLogin() {
    setTimeout(() => {
      console.log("Demo login successful");
      localStorage.setItem("access_token", "demo_token_" + Date.now());
      this.isLoading = false;
      this.router.navigate(["/admin"]);
    }, 1000); // Simulate loading time
  }
}
