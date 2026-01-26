import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { EventLog } from '../../services/event-log.service';

@Component({
  selector: 'app-event-log-detail-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
  ],
  template: `
    <h2 mat-dialog-title>
      <mat-icon>description</mat-icon>
      Event Log Details
    </h2>
    <mat-dialog-content>
      <div class="detail-section">
        <div class="detail-row">
          <span class="label">Timestamp:</span>
          <span class="value">{{ formatTimestamp(data.timestamp) }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Badge Number:</span>
          <mat-chip>{{ data.badge_number }}</mat-chip>
        </div>
        <div class="detail-row">
          <span class="label">Event Type:</span>
          <mat-chip [color]="getEventTypeColor(getEventType(data.log))">
            {{ getEventType(data.log) }}
          </mat-chip>
        </div>
        <div class="detail-row log-message">
          <span class="label">Log Message:</span>
          <div class="log-content">{{ data.log }}</div>
        </div>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="close()">Close</button>
    </mat-dialog-actions>
  `,
  styles: [`
    h2[mat-dialog-title] {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      padding: 16px 24px;

      mat-icon {
        color: var(--sys-primary);
      }
    }

    mat-dialog-content {
      padding: 0 24px 24px;
      min-width: 400px;
    }

    .detail-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .detail-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;

      .label {
        font-weight: 500;
        color: var(--sys-on-surface-variant);
        min-width: 120px;
        flex-shrink: 0;
      }

      .value {
        color: var(--sys-on-surface);
      }

      &.log-message {
        flex-direction: column;

        .log-content {
          background: var(--sys-surface-variant);
          padding: 16px;
          border-radius: 8px;
          font-family: 'Roboto Mono', monospace;
          font-size: 13px;
          line-height: 1.6;
          white-space: pre-wrap;
          word-break: break-word;
          max-height: 300px;
          overflow-y: auto;
        }
      }
    }

    mat-dialog-actions {
      padding: 8px 24px 16px;
    }
  `]
})
export class EventLogDetailDialogComponent {
  private dialogRef = inject(MatDialogRef<EventLogDetailDialogComponent>);
  data: EventLog = inject(MAT_DIALOG_DATA);

  close() {
    this.dialogRef.close();
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
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
    if (lowerLog.includes('license')) return 'license';
    return 'info';
  }

  getEventTypeColor(type: string): string {
    switch (type) {
      case 'employee': return 'primary';
      case 'timeclock': return 'accent';
      case 'department': return 'primary';
      case 'orgunit': return 'accent';
      case 'holiday': return 'primary';
      case 'user': return 'warn';
      case 'report': return 'accent';
      case 'license': return 'primary';
      default: return '';
    }
  }
}
