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
  private baseUrl = 'event_logs';

  /**
   * Create a new event log entry
   */
  createEventLog(eventLog: EventLogBase): Observable<EventLog> {
    return this.http.post<EventLog>(`${this.baseUrl}`, eventLog);
  }

  /**
   * Get event logs with optional filtering
   */
  getEventLogs(
    startDate?: Date,
    endDate?: Date,
    badgeNumber?: string,
    limit?: number,
    offset?: number
  ): Observable<EventLog[]> {
    let params = new HttpParams();
    
    if (startDate) {
      params = params.set('start_date', startDate.toISOString());
    }
    if (endDate) {
      params = params.set('end_date', endDate.toISOString());
    }
    if (badgeNumber) {
      params = params.set('badge_number', badgeNumber);
    }
    if (limit !== undefined) {
      params = params.set('limit', limit.toString());
    }
    if (offset !== undefined) {
      params = params.set('offset', offset.toString());
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
   * Get event logs by badge number
   */
  getEventLogsByBadgeNumber(badgeNumber: string): Observable<EventLog[]> {
    return this.http.get<EventLog[]>(`${this.baseUrl}/user/${badgeNumber}`);
  }

  /**
   * Get recent event logs (last 100 entries)
   */
  getRecentEventLogs(): Observable<EventLog[]> {
    return this.getEventLogs(undefined, undefined, undefined, 100, 0);
  }
}
