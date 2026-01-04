import { HttpEvent, HttpHandlerFn, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, switchMap, filter, take } from 'rxjs/operators';
import { UserService } from '../services/user.service';
import { PermissionService } from '../services/permission.service';
import { Router } from '@angular/router';

// Global state to handle concurrent refresh attempts
let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

/**
 * Interceptor that handles expired access tokens by automatically refreshing them
 * and retrying the original request.
 */
export function authRefreshInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  const userService = inject(UserService);
  const permissionService = inject(PermissionService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Check if this is an unauthorized error (401) and not the refresh endpoint itself
      if (error.status === 401 && !req.url.includes('/users/refresh')) {
        // Get current access token to check if we have one
        const currentToken = localStorage.getItem('access_token');

        if (currentToken) {
          return handleTokenRefresh(req, next, userService, permissionService, router);
        }
      }

      // For all other errors, just pass them through
      return throwError(() => error);
    })
  );
}

/**
 * Handles token refresh logic with concurrent request handling
 */
function handleTokenRefresh(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
  userService: UserService,
  permissionService: PermissionService,
  router: Router
): Observable<HttpEvent<unknown>> {
  if (!isRefreshing) {
    isRefreshing = true;
    refreshTokenSubject.next(null);

    return userService.refreshToken().pipe(
      switchMap((response) => {
        isRefreshing = false;
        refreshTokenSubject.next(response.access_token);

        // Update the stored access token
        localStorage.setItem('access_token', response.access_token);

        // Clone the original request with the new token
        return next(addTokenToRequest(req, response.access_token));
      }),
      catchError((refreshError) => {
        isRefreshing = false;
        refreshTokenSubject.next(null);

        // Refresh failed, clear tokens, permissions, and redirect to frontpage
        localStorage.removeItem('access_token');
        permissionService.clearPermissions();
        router.navigate(['/']);
        return throwError(() => refreshError);
      })
    );
  } else {
    // If a refresh is already in progress, wait for it to complete
    return refreshTokenSubject.pipe(
      filter(token => token !== null),
      take(1),
      switchMap(token => next(addTokenToRequest(req, token)))
    );
  }
}

/**
 * Helper function to add authorization token to request
 */
function addTokenToRequest(req: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });
}