import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { HolidayGroup } from './holiday-group.service';
import { OrgUnit } from './org-unit.service';
import { Department } from './department.service';

export interface Employee {
  id?: number;
  badge_number: string;
  first_name: string;
  last_name: string;
  payroll_type: string;
  payroll_sync: string;
  workweek_type: string;
  time_type: boolean;
  allow_clocking: boolean;
  allow_delete: boolean;
  manager?: Employee;
  holiday_group?: HolidayGroup;
  org_unit: OrgUnit;
  departments?: Department[];
}

export interface EmployeeBase {
  badge_number: string;
  first_name: string;
  last_name: string;
  payroll_type: string;
  payroll_sync: string;
  workweek_type: string;
  time_type: boolean;
  allow_clocking: boolean;
  allow_delete: boolean;
  holiday_group_id?: number;
  org_unit_id: number;
  manager_id?: number;
}

/**
 * Service for handling employee operations
 */
@Injectable({ providedIn: 'root' })
export class EmployeeService {
  private http = inject(HttpClient);
  private baseUrl = 'employees';

  /**
   * Create a new employee
   * @param employee The employee data to create
   * @returns The created employee
   */
  createEmployee(employee: EmployeeBase): Observable<Employee> {
    return this.http.post<Employee>(`${this.baseUrl}`, employee);
  }

  /**
   * Get all employees
   * @returns An array of employees
   */
  getEmployees(): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}`);
  }

  /**
   * Get all employees matching search criteria
   * @param department_name Optional department name to filter by
   * @param org_unit_name Optional org unit name to filter by
   * @param holiday_group_name Optional holiday group name to filter by
   * @param badge_number Optional badge number to filter by
   * @param first_name Optional first name to filter by
   * @param last_name Optional last name to filter by
   * @returns An array of employees matching the search criteria
   */
  getEmployeesByCriteria(
    department_name?: string,
    org_unit_name?: string,
    holiday_group_name?: string,
    badge_number?: string,
    first_name?: string,
    last_name?: string
  ): Observable<Employee[]> {
    let params = new HttpParams();
    if (department_name) {
      params = params.set('department_name', department_name);
    }
    if (org_unit_name) {
      params = params.set('org_unit_name', org_unit_name);
    }
    if (holiday_group_name) {
      params = params.set('holiday_group_name', holiday_group_name);
    }
    if (badge_number) {
      params = params.set('badge_number', badge_number);
    }
    if (first_name) {
      params = params.set('first_name', first_name);
    }
    if (last_name) {
      params = params.set('last_name', last_name);
    }

    return this.http.get<Employee[]>(`${this.baseUrl}/search`, { params });
  }

  /**
   * Get employee by ID
   * @param id The ID of the employee to retrieve
   * @returns The employee with the specified ID
   */
  getEmployeeById(id: number): Observable<Employee> {
    return this.http.get<Employee>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get employee by badge number
   * @param badgeNumber The badge number of the employee to retrieve
   * @returns The employee with the specified badge number
   */
  getEmployeeByBadgeNumber(badgeNumber: string): Observable<Employee> {
    return this.http.get<Employee>(`${this.baseUrl}/badge/${badgeNumber}`);
  }

  /**
   * Update an existing employee
   * @param id The ID of the employee to update
   * @param employee The updated employee data
   * @returns The updated employee
   */
  updateEmployee(id: number, employee: EmployeeBase): Observable<Employee> {
    return this.http.put<Employee>(`${this.baseUrl}/${id}`, employee);
  }

  /**
   * Update employee badge number
   * @param id The ID of the employee to update
   * @param badgeNumber The new badge number
   * @returns The updated employee
   */
  updateEmployeeBadgeNumber(
    id: number,
    badgeNumber: string
  ): Observable<Employee> {
    return this.http.put<Employee>(`${this.baseUrl}/${id}/badge_number`, {
      badge_number: badgeNumber,
    });
  }

  /**
   * Delete an employee
   * @param id The ID of the employee to delete
   * @returns An observable indicating the completion of the delete operation
   */
  deleteEmployee(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
