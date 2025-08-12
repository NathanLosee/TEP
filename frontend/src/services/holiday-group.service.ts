import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Holiday {
  name: string;
  start_date: string;
  end_date: string;
  holiday_group_id: number;
}

export interface HolidayBase {
  name: string;
  start_date: string;
  end_date: string;
}

export interface HolidayGroup {
  id: number;
  name: string;
}

export interface HolidayGroupWithDetails extends HolidayGroup {
  holidays: Holiday[];
  employees: Array<{
    id: number;
    badge_number: string;
    first_name: string;
    last_name: string;
  }>;
}

export interface HolidayGroupBase {
  name: string;
}

/**
 * Service for handling holiday group operations
 */
@Injectable({ providedIn: 'root' })
export class HolidayGroupService {
  private http = inject(HttpClient);
  private baseUrl = 'holiday_groups';

  /**
   * Create a new holiday group
   */
  createHolidayGroup(holidayGroup: HolidayGroupBase): Observable<HolidayGroup> {
    return this.http.post<HolidayGroup>(`${this.baseUrl}`, holidayGroup);
  }

  /**
   * Get all holiday groups
   */
  getHolidayGroups(): Observable<HolidayGroup[]> {
    return this.http.get<HolidayGroup[]>(`${this.baseUrl}`);
  }

  /**
   * Get holiday group by ID with details
   */
  getHolidayGroupById(id: number): Observable<HolidayGroupWithDetails> {
    return this.http.get<HolidayGroupWithDetails>(`${this.baseUrl}/${id}`);
  }

  /**
   * Update an existing holiday group
   */
  updateHolidayGroup(id: number, holidayGroup: HolidayGroupBase): Observable<HolidayGroup> {
    return this.http.put<HolidayGroup>(`${this.baseUrl}/${id}`, holidayGroup);
  }

  /**
   * Delete a holiday group
   */
  deleteHolidayGroup(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Add holiday to holiday group
   */
  addHoliday(holidayGroupId: number, holiday: HolidayBase): Observable<Holiday> {
    return this.http.post<Holiday>(`${this.baseUrl}/${holidayGroupId}/holidays`, holiday);
  }

  /**
   * Update holiday in holiday group
   */
  updateHoliday(holidayGroupId: number, holidayName: string, holiday: HolidayBase): Observable<Holiday> {
    return this.http.put<Holiday>(`${this.baseUrl}/${holidayGroupId}/holidays/${encodeURIComponent(holidayName)}`, holiday);
  }

  /**
   * Delete holiday from holiday group
   */
  deleteHoliday(holidayGroupId: number, holidayName: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${holidayGroupId}/holidays/${encodeURIComponent(holidayName)}`);
  }
}
