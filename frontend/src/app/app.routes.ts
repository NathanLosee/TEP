import { Routes } from '@angular/router';
import { NavTabComponent } from './navtab/navtab.component';
import { NavPanelComponent } from './navpanel/navpanel.component';
import { TimeclockComponent } from './timeclock/timeclock.component';

export const routes: Routes = [
  {
    title: 'Login',
    path: '',
    component: NavTabComponent,
  },
  {
    title: 'Admin',
    path: 'admin',
    component: NavPanelComponent,
    children: [
      {
        title: 'Timeclock',
        path: 'timeclock',
        component: TimeclockComponent,
      },
    ],
  },
];
