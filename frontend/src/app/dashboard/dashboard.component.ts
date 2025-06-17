import { Component, OnInit, OnDestroy, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { Router, RouterModule } from "@angular/router";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatGridListModule } from "@angular/material/grid-list";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { TimeclockService } from "../../services/timeclock.service";
import { UserService } from "../../services/user.service";
import { interval, Subscription } from "rxjs";

@Component({
  selector: "app-dashboard",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatGridListModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  templateUrl: "./dashboard.component.html",
  styleUrl: "./dashboard.component.scss",
})
export class DashboardComponent implements OnInit, OnDestroy {
  private timeclockService = inject(TimeclockService);
  private userService = inject(UserService);
  private snackBar = inject(MatSnackBar);
  private router = inject(Router);
  private clockSubscription?: Subscription;

  currentDateTime = new Date();
  badgeNumber = "";
  isLoading = false;
  clockedInEmployees: any[] = [];
  isAuthenticated = false;

  ngOnInit() {
    // Check authentication status
    this.checkAuthStatus();
    // Update clock every second
    this.clockSubscription = interval(1000).subscribe(() => {
      this.currentDateTime = new Date();
    });
  }

  ngOnDestroy() {
    if (this.clockSubscription) {
      this.clockSubscription.unsubscribe();
    }
  }

  quickClockInOut() {
    if (!this.badgeNumber.trim()) {
      this.showSnackBar("Please enter a badge number");
      return;
    }

    this.isLoading = true;
    this.timeclockService.timeclock(this.badgeNumber).subscribe({
      next: (response) => {
        this.showSnackBar(response.message, "success");
        this.badgeNumber = "";
        this.isLoading = false;
      },
      error: (error) => {
        this.showSnackBar(error.error?.detail || "An error occurred", "error");
        this.isLoading = false;
      },
    });
  }

  checkStatus() {
    if (!this.badgeNumber.trim()) {
      this.showSnackBar("Please enter a badge number");
      return;
    }

    this.isLoading = true;
    this.timeclockService.checkStatus(this.badgeNumber).subscribe({
      next: (response) => {
        this.showSnackBar(`Status: ${response.message}`, "info");
        this.isLoading = false;
      },
      error: (error) => {
        this.showSnackBar(error.error?.detail || "An error occurred", "error");
        this.isLoading = false;
      },
    });
  }

  checkAuthStatus() {
    this.isAuthenticated = this.userService.isAuthenticated();
  }

  goToLogin() {
    console.log("Navigating to login...");
    this.router
      .navigate(["/login"])
      .then((success) => {
        console.log("Navigation success:", success);
      })
      .catch((error) => {
        console.log("Navigation error:", error);
      });
  }

  goToAdminDashboard() {
    if (this.isAuthenticated) {
      this.router.navigate(["/admin"]);
    } else {
      this.goToLogin();
    }
  }

  goToEmployees() {
    if (this.isAuthenticated) {
      this.router.navigate(["/admin/employees"]);
    } else {
      this.goToLogin();
    }
  }

  goToReports() {
    if (this.isAuthenticated) {
      this.router.navigate(["/admin/reports"]);
    } else {
      this.goToLogin();
    }
  }

  goToDepartments() {
    if (this.isAuthenticated) {
      this.router.navigate(["/admin/departments"]);
    } else {
      this.goToLogin();
    }
  }

  goToOrgUnits() {
    if (this.isAuthenticated) {
      this.router.navigate(["/admin/org-units"]);
    } else {
      this.goToLogin();
    }
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
