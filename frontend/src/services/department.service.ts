import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Employee } from './employee.service';

export interface Department {
  id?: number;
  name: string;
  employee_count?: number;
}

/**
 * Service for handling department operations
 */
@Injectable({ providedIn: 'root' })
export class DepartmentService {
  private http = inject(HttpClient);
  private baseUrl = '/departments';

  /**
   * Create a new department
   * @param department The department data to create
   * @returns The created department
   */
  createDepartment(department: Department): Observable<Department> {
    return this.http.post<Department>(`${this.baseUrl}`, department);
  }

  /**
   * Get all departments
   * @returns An array of departments
   */
  getDepartments(): Observable<Department[]> {
    return this.http.get<Department[]>(`${this.baseUrl}`);
  }

  /**
   * Get department by ID
   * @param id The ID of the department to retrieve
   * @returns The department with the specified ID
   */
  getDepartmentById(id: number): Observable<Department> {
    return this.http.get<Department>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get employees by department
   * @param departmentId The ID of the department to retrieve employees from
   * @returns An array of employees in the specified department
   */
  getEmployeesByDepartment(departmentId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(
      `${this.baseUrl}/${departmentId}/employees`
    );
  }

  /**
   * Update an existing department
   * @param id The ID of the department to update
   * @param department The updated department data
   * @returns The updated department
   */
  updateDepartment(id: number, department: Department): Observable<Department> {
    return this.http.put<Department>(`${this.baseUrl}/${id}`, department);
  }

  /**
   * Delete a department
   * @param id The ID of the department to delete
   * @returns An observable indicating the completion of the delete operation
   */
  deleteDepartment(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Add employee to department
   * @param departmentId The ID of the department to add the employee to
   * @param employeeId The ID of the employee to add
   * @returns An array of employees in the department
   */
  addEmployeeToDepartment(
    departmentId: number,
    employeeId: number
  ): Observable<Employee[]> {
    return this.http.post<Employee[]>(
      `${this.baseUrl}/${departmentId}/employees/${employeeId}`,
      {}
    );
  }

  /**
   * Remove employee from department
   * @param departmentId The ID of the department to remove the employee from
   * @param employeeId The ID of the employee to remove
   * @returns An array of employees in the department
   */
  removeEmployeeFromDepartment(
    departmentId: number,
    employeeId: number
  ): Observable<Employee[]> {
    return this.http.delete<Employee[]>(
      `${this.baseUrl}/${departmentId}/employees/${employeeId}`
    );
  }
}
