import { Component } from "@angular/core";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatButtonModule } from "@angular/material/button";
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatListModule } from "@angular/material/list";
import { MatIconModule } from "@angular/material/icon";
import { RouterModule } from "@angular/router";

@Component({
  selector: "app-nav-admin",
  standalone: true,
  imports: [
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    RouterModule,
  ],
  template: `
    <mat-toolbar class="main-toolbar">
      <button mat-icon-button (click)="sidenav.toggle()" class="menu-button">
        <mat-icon>menu</mat-icon>
      </button>
      <div class="toolbar-title">
        <mat-icon class="app-icon">access_time</mat-icon>
        <h1>TEP Admin</h1>
      </div>
      <div class="toolbar-actions">
        <button mat-icon-button matTooltip="Notifications">
          <mat-icon>notifications</mat-icon>
        </button>
        <button mat-icon-button matTooltip="Settings">
          <mat-icon>settings</mat-icon>
        </button>
        <button mat-icon-button matTooltip="Logout" routerLink="/">
          <mat-icon>logout</mat-icon>
        </button>
      </div>
    </mat-toolbar>

    <mat-sidenav-container class="sidenav-container" autosize>
      <mat-sidenav #sidenav class="sidenav" mode="side" opened>
        <div class="sidenav-header">
          <mat-icon class="header-icon">admin_panel_settings</mat-icon>
          <div class="header-text">
            <div class="header-title">Administration</div>
            <div class="header-subtitle">Management Panel</div>
          </div>
        </div>

        <mat-nav-list class="nav-list">
          <h3 mat-subheader>Dashboard</h3>
          <a
            mat-list-item
            routerLink="/admin/dashboard"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>Overview</span>
          </a>

          <mat-divider></mat-divider>

          <h3 mat-subheader>Time Management</h3>
          <a
            mat-list-item
            routerLink="/admin/timeclock"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>schedule</mat-icon>
            <span matListItemTitle>Live Timeclock</span>
          </a>
          <a
            mat-list-item
            routerLink="/admin/time-entries"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>event_note</mat-icon>
            <span matListItemTitle>Time Entries</span>
          </a>

          <mat-divider></mat-divider>

          <h3 mat-subheader>User & Security Management</h3>
          <a
            mat-list-item
            routerLink="/admin/users"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>account_circle</mat-icon>
            <span matListItemTitle>User Accounts</span>
          </a>
          <a
            mat-list-item
            routerLink="/admin/auth-roles"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>security</mat-icon>
            <span matListItemTitle>Auth Roles</span>
          </a>

          <mat-divider></mat-divider>

          <h3 mat-subheader>Employee Management</h3>
          <a
            mat-list-item
            routerLink="/admin/employees"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>people</mat-icon>
            <span matListItemTitle>Employees</span>
          </a>
          <a
            mat-list-item
            routerLink="/admin/departments"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>business</mat-icon>
            <span matListItemTitle>Departments</span>
          </a>
          <a
            mat-list-item
            routerLink="/admin/org-units"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>account_tree</mat-icon>
            <span matListItemTitle>Org Units</span>
          </a>
          <a
            mat-list-item
            routerLink="/admin/holiday-groups"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>event</mat-icon>
            <span matListItemTitle>Holiday Groups</span>
          </a>

          <mat-divider></mat-divider>

          <h3 mat-subheader>Reports</h3>
          <a
            mat-list-item
            routerLink="/admin/reports"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>assessment</mat-icon>
            <span matListItemTitle>Time Reports</span>
          </a>
          <a
            mat-list-item
            routerLink="/admin/analytics"
            routerLinkActive="active-link"
          >
            <mat-icon matListItemIcon>analytics</mat-icon>
            <span matListItemTitle>Analytics</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>

      <mat-sidenav-content class="main-content">
        <router-outlet></router-outlet>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: `
    .main-toolbar {
      background: var(--sys-surface);
      color: var(--sys-on-surface);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 1000;
      position: relative;

      .menu-button {
        margin-right: 16px;
      }

      .toolbar-title {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;

        .app-icon {
          color: var(--sys-primary);
          font-size: 1.5rem;
          width: 1.5rem;
          height: 1.5rem;
        }

        h1 {
          margin: 0;
          font-size: 1.25rem;
          font-weight: 600;
        }
      }

      .toolbar-actions {
        display: flex;
        gap: 8px;
      }
    }

    .sidenav-container {
      width: 100%;
      height: calc(100vh - 64px);
    }

    .sidenav {
      width: 280px;
      background: var(--sys-surface-container);
      color: var(--sys-on-surface);
      border-right: 1px solid var(--sys-outline-variant);

      .sidenav-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 24px 20px;
        background: var(--sys-primary-container);
        color: var(--sys-on-primary-container);
        margin-bottom: 8px;

        .header-icon {
          font-size: 2rem;
          width: 2rem;
          height: 2rem;
        }

        .header-text {
          .header-title {
            font-size: 1.1rem;
            font-weight: 600;
            line-height: 1.2;
          }

          .header-subtitle {
            font-size: 0.875rem;
            opacity: 0.8;
            margin-top: 2px;
          }
        }
      }

      .nav-list {
        padding: 0 8px;

        h3[mat-subheader] {
          color: var(--sys-on-surface-variant);
          font-weight: 600;
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin: 24px 0 8px 16px;

          &:first-child {
            margin-top: 8px;
          }
        }

        a[mat-list-item] {
          border-radius: 8px;
          margin: 4px 0;
          transition: background-color 0.2s ease;

          &.active-link {
            background: var(--sys-primary-container);
            color: var(--sys-on-primary-container);

            mat-icon {
              color: var(--sys-primary);
            }
          }

          mat-icon {
            color: var(--sys-on-surface-variant);
            margin-right: 16px;
          }

          span {
            font-weight: 500;
          }
        }
      }
    }

    .main-content {
      background: var(--sys-surface);
      min-height: 100%;
    }

    @media (max-width: 768px) {
      .sidenav {
        width: 100%;
      }

      .toolbar-title h1 {
        font-size: 1.1rem;
      }
    }
  `,
})
export class NavAdminComponent {}
