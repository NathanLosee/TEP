import { Routes } from '@angular/router';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { NavFrontpageComponent } from './nav-frontpage/nav-frontpage.component';
import { NavAdminComponent } from './nav-admin/nav-admin.component';
import { EmployeeManagementComponent } from './employee-management/employee-management.component';
import { TimeclockEntriesManagementComponent } from './timeclock-entries-management/timeclock-entries-management.component';
import { DepartmentManagementComponent } from './department-management/department-management.component';
import { OrgUnitManagementComponent } from './org-unit-management/org-unit-management.component';
import { HolidayGroupManagementComponent } from './holiday-group-management/holiday-group-management.component';
import { ReportsComponent } from './reports/reports.component';
import { UserManagementComponent } from './user-management/user-management.component';
import { AuthRoleManagementComponent } from './auth-role-management/auth-role-management.component';
import { EventLogManagementComponent } from './event-log-management/event-log-management.component';
import { RegisteredBrowserManagementComponent } from './registered-browser-management/registered-browser-management.component';
import { LicenseManagementComponent } from './license-management/license-management.component';
import { SystemSettingsComponent } from './system-settings/system-settings.component';

export const routes: Routes = [
  {
    title: 'TEP Timeclock - Dashboard',
    path: '',
    component: NavFrontpageComponent,
  },
  {
    title: 'TEP Admin',
    path: 'admin',
    component: NavAdminComponent,
    children: [
      {
        title: 'Admin Dashboard',
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full',
      },
      {
        title: 'Admin Dashboard',
        path: 'dashboard',
        component: AdminDashboardComponent,
      },
      {
        title: 'Timeclock Entries',
        path: 'timeclock-entries',
        component: TimeclockEntriesManagementComponent,
      },
      {
        title: 'User Accounts',
        path: 'users',
        component: UserManagementComponent,
      },
      {
        title: 'Auth Roles',
        path: 'auth-roles',
        component: AuthRoleManagementComponent,
      },
      {
        title: 'Employee Management',
        path: 'employees',
        component: EmployeeManagementComponent,
      },
      {
        title: 'Departments',
        path: 'departments',
        component: DepartmentManagementComponent,
      },
      {
        title: 'Organizational Units',
        path: 'org-units',
        component: OrgUnitManagementComponent,
      },
      {
        title: 'Holiday Groups',
        path: 'holiday-groups',
        component: HolidayGroupManagementComponent,
      },
      {
        title: 'Registered Browsers',
        path: 'registered-browsers',
        component: RegisteredBrowserManagementComponent,
      },
      {
        title: 'Time Reports',
        path: 'reports',
        component: ReportsComponent,
      },
      {
        title: 'Event Logs',
        path: 'event-logs',
        component: EventLogManagementComponent,
      },
      {
        title: 'License Management',
        path: 'license',
        component: LicenseManagementComponent,
      },
      {
        title: 'System Settings',
        path: 'settings',
        component: SystemSettingsComponent,
      },
    ],
  },
  {
    title: 'Not Found',
    path: '**',
    redirectTo: '',
  },
];
