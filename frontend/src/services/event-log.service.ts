import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EventLog {
  id: number;
  log: string;
  timestamp: string;
  badge_number: string;
}

export interface EventLogBase {
  log: string;
  badge_number: string;
}

/**
 * Service for handling event log operations
 */
@Injectable({ providedIn: 'root' })
export class EventLogService {
  private http = inject(HttpClient);
  private baseUrl = 'event_log';

  /**
   * Create a new event log entry
   */
  createEventLog(eventLog: EventLogBase): Observable<EventLog> {
    return this.http.post<EventLog>(`${this.baseUrl}`, eventLog);
  }

  /**
   * Get event logs with optional filtering
   * Matches backend API: start_timestamp, end_timestamp, badge_number, log_filter
   */
  getEventLogs(
    startTimestamp: string,
    endTimestamp: string,
    badgeNumber?: string,
    logFilter?: string
  ): Observable<EventLog[]> {
    let params = new HttpParams()
      .set('start_timestamp', startTimestamp)
      .set('end_timestamp', endTimestamp);

    if (badgeNumber) {
      params = params.set('badge_number', badgeNumber);
    }
    if (logFilter) {
      params = params.set('log_filter', logFilter);
    }

    return this.http.get<EventLog[]>(`${this.baseUrl}`, { params });
  }

  /**
   * Get event log by ID
   */
  getEventLogById(id: number): Observable<EventLog> {
    return this.http.get<EventLog>(`${this.baseUrl}/${id}`);
  }

  /**
   * Delete an event log entry
   */
  deleteEventLog(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get recent event logs (last N days)
   * @param days Number of days to look back (default: 7)
   */
  getRecentEventLogs(days: number = 7): Observable<EventLog[]> {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    return this.getEventLogs(
      startDate.toISOString(),
      endDate.toISOString()
    );
  }
}
