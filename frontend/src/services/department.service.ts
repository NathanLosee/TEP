import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Department {
  id: number;
  name: string;
}

export interface DepartmentWithEmployees extends Department {
  employees: Array<{
    id: number;
    badge_number: string;
    first_name: string;
    last_name: string;
  }>;
}

export interface DepartmentBase {
  name: string;
}

/**
 * Service for handling department operations
 */
@Injectable({ providedIn: 'root' })
export class DepartmentService {
  private http = inject(HttpClient);
  private baseUrl = 'departments';

  /**
   * Create a new department
   */
  createDepartment(department: DepartmentBase): Observable<Department> {
    return this.http.post<Department>(`${this.baseUrl}`, department);
  }

  /**
   * Get all departments
   */
  getDepartments(): Observable<Department[]> {
    return this.http.get<Department[]>(`${this.baseUrl}`);
  }

  /**
   * Get department by ID
   */
  getDepartmentById(id: number): Observable<DepartmentWithEmployees> {
    return this.http.get<DepartmentWithEmployees>(`${this.baseUrl}/${id}`);
  }

  /**
   * Update an existing department
   */
  updateDepartment(id: number, department: DepartmentBase): Observable<Department> {
    return this.http.put<Department>(`${this.baseUrl}/${id}`, department);
  }

  /**
   * Delete a department
   */
  deleteDepartment(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Add employee to department
   */
  addEmployeeToDepartment(departmentId: number, employeeId: number): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/${departmentId}/employees/${employeeId}`, {});
  }

  /**
   * Remove employee from department
   */
  removeEmployeeFromDepartment(departmentId: number, employeeId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${departmentId}/employees/${employeeId}`);
  }
}
