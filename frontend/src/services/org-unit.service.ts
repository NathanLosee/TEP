import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface OrgUnit {
  id: number;
  name: string;
}

export interface OrgUnitWithEmployees extends OrgUnit {
  employees: Array<{
    id: number;
    badge_number: string;
    first_name: string;
    last_name: string;
  }>;
}

export interface OrgUnitBase {
  name: string;
}

/**
 * Service for handling organizational unit operations
 */
@Injectable({ providedIn: 'root' })
export class OrgUnitService {
  private http = inject(HttpClient);
  private baseUrl = 'org_units';

  /**
   * Create a new organizational unit
   */
  createOrgUnit(orgUnit: OrgUnitBase): Observable<OrgUnit> {
    return this.http.post<OrgUnit>(`${this.baseUrl}`, orgUnit);
  }

  /**
   * Get all organizational units
   */
  getOrgUnits(): Observable<OrgUnit[]> {
    return this.http.get<OrgUnit[]>(`${this.baseUrl}`);
  }

  /**
   * Get organizational unit by ID
   */
  getOrgUnitById(id: number): Observable<OrgUnitWithEmployees> {
    return this.http.get<OrgUnitWithEmployees>(`${this.baseUrl}/${id}`);
  }

  /**
   * Update an existing organizational unit
   */
  updateOrgUnit(id: number, orgUnit: OrgUnitBase): Observable<OrgUnit> {
    return this.http.put<OrgUnit>(`${this.baseUrl}/${id}`, orgUnit);
  }

  /**
   * Delete an organizational unit
   */
  deleteOrgUnit(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
