import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { RouterModule } from '@angular/router';
import { interval, Subscription } from 'rxjs';
import { EventLogService, EventLog } from '../../services/event-log.service';
import { UserService } from '../../services/user.service';

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
  private eventLogService = inject(EventLogService);
  private userService = inject(UserService);

  currentDateAndTime = Date.now();
  recentActivity: {
    type: string;
    action: string;
    detail: string;
    time: string;
    icon: string;
  }[] = [];
  isLoadingEvents = true;

  ngOnInit() {
    // Update the current date and time every minute
    const timer = interval(60000);
    this.clockSubscription = timer.subscribe(() => {
      this.currentDateAndTime = Date.now();
    });

    // Load recent event logs
    this.loadRecentEventLogs();
  }

  loadRecentEventLogs() {
    this.isLoadingEvents = true;
    this.eventLogService.getRecentEventLogs(7).subscribe({
      next: (logs) => {
        this.recentActivity = this.transformEventLogs(logs);
        this.isLoadingEvents = false;
      },
      error: (error) => {
        console.error('Error loading event logs:', error);
        this.isLoadingEvents = false;
      },
    });
  }

  transformEventLogs(logs: EventLog[]): {
    type: string;
    action: string;
    detail: string;
    time: string;
    icon: string;
  }[] {
    return logs
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 10)
      .map((log) => {
        const type = this.getEventType(log.log);
        return {
          type,
          action: this.extractAction(log.log),
          detail: this.extractDetail(log.log),
          time: this.getRelativeTime(log.timestamp),
          icon: this.getActivityIcon(type),
        };
      });
  }

  getEventType(logMessage: string): string {
    const lowerLog = logMessage.toLowerCase();
    if (lowerLog.includes('employee')) return 'employee';
    if (lowerLog.includes('timeclock') || lowerLog.includes('clock')) return 'timeclock';
    if (lowerLog.includes('department')) return 'department';
    if (lowerLog.includes('org unit')) return 'orgunit';
    if (lowerLog.includes('holiday')) return 'holiday';
    if (lowerLog.includes('user') || lowerLog.includes('auth') || lowerLog.includes('role')) return 'user';
    if (lowerLog.includes('report')) return 'report';
    return 'info';
  }

  extractAction(logMessage: string): string {
    // Extract the main action (first part of the log message)
    const parts = logMessage.split(' - ');
    return parts[0].trim();
  }

  extractDetail(logMessage: string): string {
    // Extract details (part after the dash, if any)
    const parts = logMessage.split(' - ');
    return parts.length > 1 ? parts.slice(1).join(' - ').trim() : '';
  }

  getRelativeTime(timestamp: string): string {
    const now = new Date();
    const eventTime = new Date(timestamp);
    const diffMs = now.getTime() - eventTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    return eventTime.toLocaleDateString();
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
      case 'holiday':
        return 'event';
      case 'user':
        return 'admin_panel_settings';
      case 'report':
        return 'assessment';
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
      case 'holiday':
        return 'primary';
      case 'user':
        return 'warn';
      case 'report':
        return 'accent';
      default:
        return 'primary';
    }
  }
}
