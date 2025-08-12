import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AccessResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
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
  id: number;
  name: string;
  permissions: Array<{ resource: string }>;
}

/**
 * Service for handling user operations including authentication and user management
 */
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private baseUrl = 'users';

  /**
   * Login a user
   */
  login(loginData: FormData): Observable<AccessResponse> {
    return this.http.post<AccessResponse>(`${this.baseUrl}/login`, loginData);
  }

  /**
   * Logout a user
   */
  logout(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.baseUrl}/logout`, {});
  }

  /**
   * Refresh access token
   */
  refreshToken(): Observable<AccessResponse> {
    return this.http.post<AccessResponse>(`${this.baseUrl}/refresh`, {});
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
      return payload.sub || null;
    } catch {
      return null;
    }
  }

  constructor() {}
}
