import { Component } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { ClockerComponent } from '../clocker/clocker.component';
import { LoginComponent } from '../login/login.component';

@Component({
  selector: 'app-navtab',
  standalone: true,
  imports: [MatTabsModule, MatIconModule, ClockerComponent, LoginComponent],
  template: `
    <mat-tab-group dynamicHeight animationDuration="200ms">
      <mat-tab
        ><ng-template mat-tab-label>
          <mat-icon>alarm_on</mat-icon>
        </ng-template>
        <app-clocker></app-clocker>
      </mat-tab>
      <mat-tab
        ><ng-template mat-tab-label>
          <mat-icon>account_circle</mat-icon>
        </ng-template>
        <app-login></app-login>
      </mat-tab>
    </mat-tab-group>
  `,
  styles: `
    mat-tab-group {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
    }
  `,
})
export class NavTabComponent {}
