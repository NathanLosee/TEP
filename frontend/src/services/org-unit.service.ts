import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Employee } from './employee.service';

export interface OrgUnit {
  id?: number;
  name: string;
}

/**
 * Service for handling organizational unit operations
 */
@Injectable({ providedIn: 'root' })
export class OrgUnitService {
  private http = inject(HttpClient);
  private baseUrl = '/org_units';

  /**
   * Create a new organizational unit
   * @param orgUnit The organizational unit data to create
   * @returns The created organizational unit
   */
  createOrgUnit(orgUnit: OrgUnit): Observable<OrgUnit> {
    return this.http.post<OrgUnit>(`${this.baseUrl}`, orgUnit);
  }

  /**
   * Get all organizational units
   * @returns An array of organizational units
   */
  getOrgUnits(): Observable<OrgUnit[]> {
    return this.http.get<OrgUnit[]>(`${this.baseUrl}`);
  }

  /**
   * Get organizational unit by ID
   * @param id The ID of the organizational unit to retrieve
   * @returns The organizational unit with the specified ID
   */
  getOrgUnitById(id: number): Observable<OrgUnit> {
    return this.http.get<OrgUnit>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get employees by org unit
   * @param orgUnitId The ID of the org unit to retrieve employees from
   * @returns An array of employees in the specified org unit
   */
  getEmployeesByOrgUnit(orgUnitId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/${orgUnitId}/employees`);
  }

  /**
   * Update an existing organizational unit
   * @param id The ID of the organizational unit to update
   * @param orgUnit The updated organizational unit data
   * @returns The updated organizational unit
   */
  updateOrgUnit(id: number, orgUnit: OrgUnit): Observable<OrgUnit> {
    return this.http.put<OrgUnit>(`${this.baseUrl}/${id}`, orgUnit);
  }

  /**
   * Delete an organizational unit
   * @param id The ID of the organizational unit to delete
   * @returns An observable indicating the completion of the delete operation
   */
  deleteOrgUnit(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
