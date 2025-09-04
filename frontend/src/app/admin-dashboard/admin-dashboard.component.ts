import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { RouterModule } from '@angular/router';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatGridListModule,
    MatChipsModule,
    MatProgressBarModule,
  ],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss',
})
export class AdminDashboardComponent implements OnInit {
  private clockSubscription?: Subscription;

  currentDateAndTime = Date.now();

  recentActivity = [
    {
      type: 'employee',
      action: 'New employee added',
      detail: 'Sarah Johnson - IT Department',
      time: '2 hours ago',
      icon: 'person_add',
    },
    {
      type: 'timeclock',
      action: 'Bulk clock-out processed',
      detail: '45 employees - End of shift',
      time: '3 hours ago',
      icon: 'schedule',
    },
    {
      type: 'department',
      action: 'Department updated',
      detail: 'Manufacturing - New manager assigned',
      time: '5 hours ago',
      icon: 'business',
    },
    {
      type: 'orgunit',
      action: 'Org unit created',
      detail: 'Quality Assurance East - Atlanta, GA',
      time: '1 day ago',
      icon: 'account_tree',
    },
  ];

  ngOnInit() {
    // Update the current date and time every minute
    const timer = interval(60000);
    this.clockSubscription = timer.subscribe(() => {
      this.currentDateAndTime = Date.now();
    });
  }

  ngOnDestroy() {
    // Unsubscribe from the timer to prevent memory leaks
    if (this.clockSubscription) {
      this.clockSubscription.unsubscribe();
    }
  }

  getActivityIcon(type: string): string {
    switch (type) {
      case 'employee':
        return 'person';
      case 'timeclock':
        return 'schedule';
      case 'department':
        return 'business';
      case 'orgunit':
        return 'account_tree';
      default:
        return 'info';
    }
  }

  getActivityColor(type: string): string {
    switch (type) {
      case 'employee':
        return 'primary';
      case 'timeclock':
        return 'accent';
      case 'department':
        return 'primary';
      case 'orgunit':
        return 'accent';
      default:
        return 'primary';
    }
  }
}
