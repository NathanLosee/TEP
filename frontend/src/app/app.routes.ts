import { Routes } from '@angular/router';
import { NavFrontpageComponent } from './nav-frontpage/nav-frontpage.component';
import { NavAdminComponent } from './nav-admin/nav-admin.component';
import { TimeclockEntriesComponent } from './timeclock-entries/timeclock-entries.component';

export const routes: Routes = [
  {
    title: 'Login',
    path: '',
    component: NavFrontpageComponent,
  },
  {
    title: 'Admin',
    path: 'admin',
    component: NavAdminComponent,
    children: [
      {
        title: 'Timeclock',
        path: 'timeclock',
        component: TimeclockEntriesComponent,
      },
    ],
  },
];
