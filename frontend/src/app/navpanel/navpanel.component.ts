import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-navpanel',
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
    <mat-toolbar>
      <button mat-icon-button (click)="sidenav.toggle()">
        <mat-icon>menu</mat-icon>
      </button>
      <h1>TEP</h1>
    </mat-toolbar>
    <mat-sidenav-container class="sidenav-container" autosize>
      <mat-sidenav #sidenav class="sidenav" mode="side" opened>
        <mat-toolbar>Navigation</mat-toolbar>
        <mat-nav-list>
          <a mat-list-item routerLink="timeclock">Link 1</a>
          <a mat-list-item routerLink="timeclock">Link 2</a>
        </mat-nav-list>
      </mat-sidenav>
      <mat-sidenav-content>
        <router-outlet></router-outlet>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: `
    .sidenav-container {
      width: 100%;
      height: 100vh;
    }
    
    .sidenav {
      width: 150px;
    }

    mat-list-item {
      text-align: center;
    }
    
    .mat-toolbar {
      background: inherit;
    }

    .sidenav {
      background-color: var(--sys-secondary-container);
      color: var(--sys-on-secondary-container);
    }
  `,
})
export class NavPanelComponent {}
