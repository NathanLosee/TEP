import { Routes } from '@angular/router';
import { ClockerComponent } from './clocker/clocker.component';

export const routes: Routes = [
  {
    path: '',
    component: ClockerComponent,
    title: 'Timeclock',
  },
];
