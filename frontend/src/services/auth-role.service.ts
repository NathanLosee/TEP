import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { User } from './user.service';

export interface Permission {
  resource: string;
}

export interface AuthRole {
  id?: number;
  name: string;
  permissions: Permission[];
}

export interface AuthRoleBase {
  name: string;
  permissions: Permission[];
}

/**
 * Service for handling Auth Role operations
 */
@Injectable({ providedIn: 'root' })
export class AuthRoleService {
  private http = inject(HttpClient);
  private baseUrl = 'auth_roles';

  /**
   * Create a new auth role
   */
  createAuthRole(authRole: AuthRoleBase): Observable<AuthRole> {
    return this.http.post<AuthRole>(`${this.baseUrl}`, authRole);
  }

  /**
   * Get all auth roles
   */
  getAuthRoles(): Observable<AuthRole[]> {
    return this.http.get<AuthRole[]>(`${this.baseUrl}`);
  }

  /**
   * Get auth role by ID
   */
  getAuthRoleById(id: number): Observable<AuthRole> {
    return this.http.get<AuthRole>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get users assigned to an auth role
   */
  getUsersByAuthRole(authRoleId: number): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/${authRoleId}/users`);
  }

  /**
   * Update an existing auth role
   */
  updateAuthRole(id: number, authRole: AuthRole): Observable<AuthRole> {
    return this.http.put<AuthRole>(`${this.baseUrl}/${id}`, authRole);
  }

  /**
   * Delete an auth role
   */
  deleteAuthRole(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Assign user to auth role
   */
  assignUserToRole(authRoleId: number, userId: number): Observable<User[]> {
    return this.http.post<User[]>(
      `${this.baseUrl}/${authRoleId}/users/${userId}`,
      {}
    );
  }

  /**
   * Remove user from auth role
   */
  removeUserFromRole(authRoleId: number, userId: number): Observable<User[]> {
    return this.http.delete<User[]>(
      `${this.baseUrl}/${authRoleId}/users/${userId}`
    );
  }

  /**
   * Get all available resource scopes for permissions
   */
  getAvailableResourceScopes(): { [key: string]: string } {
    return {
      'auth_role.create': 'Create Auth Role',
      'auth_role.read': 'Read Auth Role',
      'auth_role.update': 'Update Auth Role',
      'auth_role.delete': 'Delete Auth Role',
      'auth_role.assign': 'Assign Auth Role',
      'auth_role.unassign': 'Unassign Auth Role',
      'department.create': 'Create Department',
      'department.read': 'Read Department',
      'department.update': 'Update Department',
      'department.delete': 'Delete Department',
      'department.assign': 'Assign Department',
      'department.unassign': 'Unassign Department',
      'employee.create': 'Create Employee',
      'employee.read': 'Read Employee',
      'employee.update': 'Update Employee',
      'employee.update.badge_number': 'Update Employee Badge Number',
      'employee.delete': 'Delete Employee',
      'event_log.create': 'Create Event Log',
      'event_log.read': 'Read Event Log',
      'event_log.delete': 'Delete Event Log',
      'holiday_group.create': 'Create Holiday Group',
      'holiday_group.read': 'Read Holiday Group',
      'holiday_group.update': 'Update Holiday Group',
      'holiday_group.delete': 'Delete Holiday Group',
      'org_unit.create': 'Create Org Unit',
      'org_unit.read': 'Read Org Unit',
      'org_unit.update': 'Update Org Unit',
      'org_unit.delete': 'Delete Org Unit',
      'timeclock.update': 'Update Timeclock entry',
      'timeclock.read': 'Read Timeclock entry',
      'timeclock.delete': 'Delete Timeclock entry',
      'user.create': 'Create User',
      'user.read': 'Read User',
      'user.update': 'Update User',
      'user.delete': 'Delete User',
    };
  }

  /**
   * Group permissions by category for better UX
   */
  getPermissionsByCategory(): {
    [category: string]: { [key: string]: string };
  } {
    const scopes = this.getAvailableResourceScopes();
    const categories: { [category: string]: { [key: string]: string } } = {};

    Object.entries(scopes).forEach(([key, value]) => {
      const category = key.split('.')[0];
      if (!categories[category]) {
        categories[category] = {};
      }
      categories[category][key] = value;
    });

    return categories;
  }
}
