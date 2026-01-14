import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { PermissionService } from './permission.service';

export interface AccessResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id?: number;
  badge_number: string;
}

export interface UserBase {
  badge_number: string;
  password: string;
}

export interface UserPasswordChange {
  badge_number: string;
  password: string;
  new_password: string;
}

export interface AuthRole {
  id?: number;
  name: string;
  permissions: Array<{ resource: string }>;
}

/**
 * Service for handling user operations including authentication and user management
 */
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private permissionService = inject(PermissionService);
  private baseUrl = '/users';

  /**
   * Login a user and set permissions
   */
  login(loginData: FormData): Observable<AccessResponse> {
    return this.http.post<AccessResponse>(`${this.baseUrl}/login`, loginData).pipe(
      tap(response => {
        // Decode token and extract permissions
        try {
          const payload = JSON.parse(atob(response.access_token.split('.')[1]));
          this.permissionService.setPermissions({
            scopes: payload.scopes || [],
            badge_number: payload.sub || ''
          });
        } catch (error) {
          console.error('Error decoding token:', error);
        }
      })
    );
  }

  /**
   * Logout a user and clear permissions
   */
  logout(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.baseUrl}/logout`, {}).pipe(
      tap(() => {
        this.permissionService.clearPermissions();
      })
    );
  }

  /**
   * Refresh access token and update permissions
   */
  refreshToken(): Observable<AccessResponse> {
    return this.http.post<AccessResponse>(`${this.baseUrl}/refresh`, {}).pipe(
      tap(response => {
        // Decode token and update permissions
        try {
          const payload = JSON.parse(atob(response.access_token.split('.')[1]));
          this.permissionService.setPermissions({
            scopes: payload.scopes || [],
            badge_number: payload.sub || ''
          });
        } catch (error) {
          console.error('Error decoding token:', error);
        }
      })
    );
  }

  /**
   * Create a new user account
   */
  createUser(userData: UserBase): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/`, userData);
  }

  /**
   * Get all users
   */
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/`);
  }

  /**
   * Get user by ID
   */
  getUserById(id: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/${id}`);
  }

  /**
   * Get user's auth roles
   */
  getUserAuthRoles(id: number): Observable<AuthRole[]> {
    return this.http.get<AuthRole[]>(`${this.baseUrl}/${id}/auth_roles`);
  }

  /**
   * Update user password
   */
  updateUserPassword(
    badgeNumber: string,
    passwordData: UserPasswordChange
  ): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/${badgeNumber}`, passwordData);
  }

  /**
   * Delete user by ID
   */
  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  /**
   * Get current user's permissions from stored token
   */
  getUserPermissions(): string[] {
    const token = localStorage.getItem('access_token');
    if (!token) return [];

    try {
      // Decode JWT token (simple decode, not verification)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.scopes || [];
    } catch {
      return [];
    }
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(permission: string): boolean {
    const permissions = this.getUserPermissions();
    return permissions.includes(permission);
  }

  /**
   * Get current user badge number from token
   */
  getCurrentUserBadge(): string | null {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.badge_number || payload.sub || null;
    } catch {
      return null;
    }
  }

  constructor() {}
}
