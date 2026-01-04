import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface UserPermissions {
  scopes: string[];
  badge_number: string;
}

/**
 * Service for managing and checking user permissions
 */
@Injectable({ providedIn: 'root' })
export class PermissionService {
  private permissionsSubject = new BehaviorSubject<UserPermissions | null>(null);
  public permissions$ = this.permissionsSubject.asObservable();

  /**
   * Set the current user's permissions (called after login)
   */
  setPermissions(permissions: UserPermissions): void {
    this.permissionsSubject.next(permissions);
  }

  /**
   * Clear permissions (called on logout)
   */
  clearPermissions(): void {
    this.permissionsSubject.next(null);
  }

  /**
   * Get current permissions synchronously
   */
  getCurrentPermissions(): UserPermissions | null {
    return this.permissionsSubject.value;
  }

  /**
   * Check if user has a specific permission
   */
  hasPermission(permission: string): boolean {
    const currentPermissions = this.permissionsSubject.value;
    if (!currentPermissions) {
      return false;
    }
    return currentPermissions.scopes.includes(permission);
  }

  /**
   * Check if user has any of the specified permissions
   */
  hasAnyPermission(permissions: string[]): boolean {
    const currentPermissions = this.permissionsSubject.value;
    if (!currentPermissions) {
      return false;
    }
    return permissions.some(permission =>
      currentPermissions.scopes.includes(permission)
    );
  }

  /**
   * Check if user has all of the specified permissions
   */
  hasAllPermissions(permissions: string[]): boolean {
    const currentPermissions = this.permissionsSubject.value;
    if (!currentPermissions) {
      return false;
    }
    return permissions.every(permission =>
      currentPermissions.scopes.includes(permission)
    );
  }

  /**
   * Observable to check if user has a specific permission
   */
  hasPermission$(permission: string): Observable<boolean> {
    return this.permissions$.pipe(
      map(perms => {
        if (!perms) return false;
        return perms.scopes.includes(permission);
      })
    );
  }

  /**
   * Observable to check if user has any of the specified permissions
   */
  hasAnyPermission$(permissions: string[]): Observable<boolean> {
    return this.permissions$.pipe(
      map(perms => {
        if (!perms) return false;
        return permissions.some(permission => perms.scopes.includes(permission));
      })
    );
  }

  /**
   * Observable to check if user has all of the specified permissions
   */
  hasAllPermissions$(permissions: string[]): Observable<boolean> {
    return this.permissions$.pipe(
      map(perms => {
        if (!perms) return false;
        return permissions.every(permission => perms.scopes.includes(permission));
      })
    );
  }

  /**
   * Get user's badge number
   */
  getBadgeNumber(): string | null {
    return this.permissionsSubject.value?.badge_number || null;
  }

  /**
   * Check if user is logged in (has permissions)
   */
  isLoggedIn(): boolean {
    return this.permissionsSubject.value !== null;
  }

  /**
   * Observable for login status
   */
  isLoggedIn$(): Observable<boolean> {
    return this.permissions$.pipe(
      map(perms => perms !== null)
    );
  }
}
