import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { LicenseService } from '../../services/license.service';

/**
 * Guard to protect admin routes that require an active license.
 * Redirects to the license activation page if no valid license exists.
 */
export const licenseGuard: CanActivateFn = () => {
  const licenseService = inject(LicenseService);
  const router = inject(Router);

  if (!licenseService.isLicensed()) {
    // Redirect to license management page
    router.navigate(['/admin/license']);
    return false;
  }

  return true;
};
