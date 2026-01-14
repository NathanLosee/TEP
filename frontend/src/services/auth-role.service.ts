import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { User } from './user.service';

export interface Permission {
  resource: string;
  description: string;
}

export interface AuthRole {
  id?: number;
  name: string;
  permissions: Permission[];
}

/**
 * Service for handling Auth Role operations
 */
@Injectable({ providedIn: 'root' })
export class AuthRoleService {
  private http = inject(HttpClient);
  private baseUrl = '/auth_roles';

  /**
   * Create a new auth role
   */
  createAuthRole(authRole: AuthRole): Observable<AuthRole> {
    return this.http.post<AuthRole>(`${this.baseUrl}`, {
      name: authRole.name,
      permissions: authRole.permissions,
    });
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
  getAvailableResourceScopes(): Permission[] {
    return [
      { resource: 'auth_role.create', description: 'Create Auth Role' },
      { resource: 'auth_role.read', description: 'Read Auth Role' },
      { resource: 'auth_role.update', description: 'Update Auth Role' },
      { resource: 'auth_role.delete', description: 'Delete Auth Role' },
      { resource: 'auth_role.assign', description: 'Assign Auth Role' },
      { resource: 'auth_role.unassign', description: 'Unassign Auth Role' },
      { resource: 'department.create', description: 'Create Department' },
      { resource: 'department.read', description: 'Read Department' },
      { resource: 'department.update', description: 'Update Department' },
      { resource: 'department.delete', description: 'Delete Department' },
      { resource: 'department.assign', description: 'Assign Department' },
      { resource: 'department.unassign', description: 'Unassign Department' },
      { resource: 'employee.create', description: 'Create Employee' },
      { resource: 'employee.read', description: 'Read Employee' },
      { resource: 'employee.update', description: 'Update Employee' },
      {
        resource: 'employee.update.badge_number',
        description: 'Update Employee Badge Number',
      },
      { resource: 'employee.delete', description: 'Delete Employee' },
      { resource: 'event_log.create', description: 'Create Event Log' },
      { resource: 'event_log.read', description: 'Read Event Log' },
      { resource: 'event_log.delete', description: 'Delete Event Log' },
      { resource: 'holiday_group.create', description: 'Create Holiday Group' },
      { resource: 'holiday_group.read', description: 'Read Holiday Group' },
      { resource: 'holiday_group.update', description: 'Update Holiday Group' },
      { resource: 'holiday_group.delete', description: 'Delete Holiday Group' },
      { resource: 'org_unit.create', description: 'Create Org Unit' },
      { resource: 'org_unit.read', description: 'Read Org Unit' },
      { resource: 'org_unit.update', description: 'Update Org Unit' },
      { resource: 'org_unit.delete', description: 'Delete Org Unit' },
      { resource: 'timeclock.update', description: 'Update Timeclock entry' },
      { resource: 'timeclock.read', description: 'Read Timeclock entry' },
      { resource: 'timeclock.delete', description: 'Delete Timeclock entry' },
      { resource: 'user.create', description: 'Create User' },
      { resource: 'user.read', description: 'Read User' },
      { resource: 'user.update', description: 'Update User' },
      { resource: 'user.delete', description: 'Delete User' },
    ];
  }

  /**
   * Group permissions by category for better UX
   */
  getPermissionsByCategory(): {
    [category: string]: Permission[];
  } {
    const scopes = this.getAvailableResourceScopes();
    const categories: { [category: string]: Permission[] } = {};

    scopes.forEach((scope) => {
      const category = scope.resource.split('.')[0];
      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(scope);
    });

    return categories;
  }
}
