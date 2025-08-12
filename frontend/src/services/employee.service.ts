import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Employee {
  id: number;
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
  manager?: {
    id: number;
    badge_number: string;
    first_name: string;
    last_name: string;
  };
  holiday_group?: {
    id: number;
    name: string;
  };
  org_unit?: {
    id: number;
    name: string;
  };
  departments?: Array<{
    id: number;
    name: string;
  }>;
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
   */
  createEmployee(employee: EmployeeBase): Observable<Employee> {
    return this.http.post<Employee>(`${this.baseUrl}`, employee);
  }

  /**
   * Get all employees
   */
  getEmployees(): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}`);
  }

  /**
   * Get employee by ID
   */
  getEmployeeById(id: number): Observable<Employee> {
    return this.http.get<Employee>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get employee by badge number
   */
  getEmployeeByBadgeNumber(badgeNumber: string): Observable<Employee> {
    return this.http.get<Employee>(`${this.baseUrl}/badge/${badgeNumber}`);
  }

  /**
   * Update an existing employee
   */
  updateEmployee(id: number, employee: EmployeeBase): Observable<Employee> {
    return this.http.put<Employee>(`${this.baseUrl}/${id}`, employee);
  }

  /**
   * Update employee badge number
   */
  updateEmployeeBadgeNumber(id: number, badgeNumber: string): Observable<Employee> {
    return this.http.put<Employee>(`${this.baseUrl}/${id}/badge_number`, { badge_number: badgeNumber });
  }

  /**
   * Delete an employee
   */
  deleteEmployee(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get employees by department
   */
  getEmployeesByDepartment(departmentId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/department/${departmentId}`);
  }

  /**
   * Get employees by org unit
   */
  getEmployeesByOrgUnit(orgUnitId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/org_unit/${orgUnitId}`);
  }

  /**
   * Get employees by holiday group
   */
  getEmployeesByHolidayGroup(holidayGroupId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/holiday_group/${holidayGroupId}`);
  }

  /**
   * Get employees by manager
   */
  getEmployeesByManager(managerId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.baseUrl}/manager/${managerId}`);
  }
}
