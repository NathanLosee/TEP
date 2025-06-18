import { Routes } from '@angular/router';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { NavFrontpageComponent } from './nav-frontpage/nav-frontpage.component';
import { NavAdminComponent } from './nav-admin/nav-admin.component';
import { EmployeeManagementComponent } from './employee-management/employee-management.component';
import { TimeEntriesComponent } from './time-entries/time-entries.component';
import { DepartmentManagementComponent } from './department-management/department-management.component';
import { OrgUnitManagementComponent } from './org-unit-management/org-unit-management.component';
import { HolidayGroupManagementComponent } from './holiday-group-management/holiday-group-management.component';
import { ReportsComponent } from './reports/reports.component';
import { AnalyticsComponent } from './analytics/analytics.component';
import { UserManagementComponent } from './user-management/user-management.component';
import { AuthRoleManagementComponent } from './auth-role-management/auth-role-management.component';

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
        title: 'Time Entries',
        path: 'time-entries',
        component: TimeEntriesComponent,
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
        title: 'Time Reports',
        path: 'reports',
        component: ReportsComponent,
      },
      {
        title: 'Analytics Dashboard',
        path: 'analytics',
        component: AnalyticsComponent,
      },
    ],
  },
  {
    title: 'Not Found',
    path: '**',
    redirectTo: '',
  },
];
