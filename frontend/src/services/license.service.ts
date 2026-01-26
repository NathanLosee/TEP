import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, map, tap } from 'rxjs';

export interface LicenseStatus {
  is_active: boolean;
  license_key: string | null;
  activated_at: string | null;
}

export interface LicenseActivationRequest {
  license_key: string;
}

export interface LicenseActivationResponse {
  id: number;
  license_key: string;
  activation_key: string;
  activated_at: string;
  is_active: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class LicenseService {
  private readonly baseUrl = '/licenses';
  private licenseStatus$ = new BehaviorSubject<LicenseStatus | null>(null);

  constructor(private http: HttpClient) {}

  /**
   * Get the current license status
   */
  getLicenseStatus(): Observable<LicenseStatus> {
    return this.http.get<LicenseStatus>(`${this.baseUrl}/status`).pipe(
      tap(status => this.licenseStatus$.next(status))
    );
  }

  /**
   * Check license status and update internal state
   */
  checkLicense(): void {
    this.http.get<LicenseStatus>(`${this.baseUrl}/status`).subscribe({
      next: (status) => {
        this.licenseStatus$.next(status);
      },
      error: (error) => {
        console.error('Failed to check license status:', error);
        this.licenseStatus$.next({ is_active: false, license_key: null, activated_at: null });
      }
    });
  }

  /**
   * Activate a license
   */
  activateLicense(licenseKey: string): Observable<LicenseActivationResponse> {
    return this.http.post<LicenseActivationResponse>(`${this.baseUrl}/activate`, {
      license_key: licenseKey,
    }).pipe(
      tap(() => {
        // Refresh license status after activation
        this.checkLicense();
      })
    );
  }

  /**
   * Deactivate the current license
   */
  deactivateLicense(): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/deactivate`).pipe(
      tap(() => {
        // Update local state
        this.licenseStatus$.next({
          is_active: false,
          license_key: null,
          activated_at: null,
        });
      })
    );
  }

  /**
   * Check if a valid license is currently active (synchronous)
   */
  isLicensed(): boolean {
    const status = this.licenseStatus$.value;
    return status ? status.is_active : false;
  }

  /**
   * Observable version of license status check
   */
  isLicensed$(): Observable<boolean> {
    return this.licenseStatus$.pipe(map((status) => status?.is_active || false));
  }
}
