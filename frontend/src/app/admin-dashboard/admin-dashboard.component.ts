import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatGridListModule } from "@angular/material/grid-list";
import { MatChipsModule } from "@angular/material/chips";
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { UserService } from "../../services/user.service";
import { AuthRoleService } from "../../services/auth-role.service";

@Component({
  selector: "app-admin-dashboard",
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatGridListModule,
    MatChipsModule,
    MatProgressBarModule,
  ],
  templateUrl: "./admin-dashboard.component.html",
  styleUrl: "./admin-dashboard.component.scss",
})
export class AdminDashboardComponent implements OnInit {
  private userService = inject(UserService);
  private authRoleService = inject(AuthRoleService);

  currentDateTime = new Date();

  // Mock data - replace with actual service calls
  dashboardStats = {
    employees: {
      total: 156,
      active: 142,
      onLeave: 8,
      newThisMonth: 12,
    },
    departments: {
      total: 8,
      active: 8,
    },
    orgUnits: {
      total: 12,
      locations: 6,
      topLevel: 3,
    },
    users: {
      total: 24,
      active: 22,
      newThisWeek: 3,
    },
    authRoles: {
      total: 6,
      totalPermissions: 28,
      assignedUsers: 18,
    },
    timeclock: {
      currentlyClocked: 89,
      totalEntriesToday: 234,
      avgHoursPerDay: 8.2,
      lateCheckIns: 5,
    },
  };

  recentActivity = [
    {
      type: "employee",
      action: "New employee added",
      detail: "Sarah Johnson - IT Department",
      time: "2 hours ago",
      icon: "person_add",
    },
    {
      type: "timeclock",
      action: "Bulk clock-out processed",
      detail: "45 employees - End of shift",
      time: "3 hours ago",
      icon: "schedule",
    },
    {
      type: "department",
      action: "Department updated",
      detail: "Manufacturing - New manager assigned",
      time: "5 hours ago",
      icon: "business",
    },
    {
      type: "orgunit",
      action: "Org unit created",
      detail: "Quality Assurance East - Atlanta, GA",
      time: "1 day ago",
      icon: "account_tree",
    },
  ];

  quickActions = [
    {
      title: "Add Employee",
      icon: "person_add",
      route: "/admin/employees",
      color: "primary",
    },
    {
      title: "View Time Entries",
      icon: "schedule",
      route: "/admin/time-entries",
      color: "accent",
    },
    {
      title: "Manage Departments",
      icon: "business",
      route: "/admin/departments",
      color: "primary",
    },
    {
      title: "Org Structure",
      icon: "account_tree",
      route: "/admin/org-units",
      color: "accent",
    },
  ];

  ngOnInit() {
    // Update clock every minute
    setInterval(() => {
      this.currentDateTime = new Date();
    }, 60000);
  }

  getActivityIcon(type: string): string {
    switch (type) {
      case "employee":
        return "person";
      case "timeclock":
        return "schedule";
      case "department":
        return "business";
      case "orgunit":
        return "account_tree";
      default:
        return "info";
    }
  }

  getActivityColor(type: string): string {
    switch (type) {
      case "employee":
        return "primary";
      case "timeclock":
        return "accent";
      case "department":
        return "primary";
      case "orgunit":
        return "accent";
      default:
        return "primary";
    }
  }
}
