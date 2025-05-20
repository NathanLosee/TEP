import { Component } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { TimeclockComponent } from '../timeclock/timeclock.component';
import { LoginComponent } from '../login/login.component';

@Component({
  selector: 'app-nav-frontpage',
  standalone: true,
  imports: [MatTabsModule, MatIconModule, LoginComponent, TimeclockComponent],
  templateUrl: './nav-frontpage.component.html',
  styleUrl: './nav-frontpage.component.scss',
})
export class NavFrontpageComponent {}
