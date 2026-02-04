import { ApplicationConfig, provideZoneChangeDetection, APP_INITIALIZER } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { baseUrlInterceptor } from '../interceptors/baseurl.interceptor';
import { formDataInterceptor } from '../interceptors/formdata.interceptor';
import { authRefreshInterceptor } from '../interceptors/auth-refresh.interceptor';
import { PermissionService } from '../services/permission.service';
import { LicenseService } from '../services/license.service';

/**
 * Initialize permissions from stored access token on app startup
 */
function initializePermissions(permissionService: PermissionService) {
  return () => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      try {
        // Decode JWT token to extract permissions
        const payload = JSON.parse(atob(accessToken.split('.')[1]));
        permissionService.setPermissions({
          scopes: payload.scopes || [],
          badge_number: payload.sub || ''
        });
      } catch (error) {
        // Token is invalid, clear it
        localStorage.removeItem('access_token');
      }
    }
  };
}

/**
 * Initialize license status on app startup
 */
function initializeLicense(licenseService: LicenseService) {
  return () => {
    licenseService.checkLicense();
  };
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimationsAsync(),
    provideHttpClient(
      withInterceptors([baseUrlInterceptor, formDataInterceptor, authRefreshInterceptor])
    ),
    {
      provide: APP_INITIALIZER,
      useFactory: initializePermissions,
      deps: [PermissionService],
      multi: true
    },
    {
      provide: APP_INITIALIZER,
      useFactory: initializeLicense,
      deps: [LicenseService],
      multi: true
    }
  ],
};
