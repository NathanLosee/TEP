import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterModule } from '@angular/router';
import { DisableIfNoPermissionDirective } from '../directives/has-permission.directive';

@Component({
  selector: 'app-nav-admin',
  standalone: true,
  imports: [
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatTooltipModule,
    RouterModule,
    DisableIfNoPermissionDirective,
  ],
  templateUrl: './nav-admin.component.html',
  styleUrl: './nav-admin.component.scss',
})
export class NavAdminComponent {}
