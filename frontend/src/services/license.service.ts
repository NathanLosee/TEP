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

interface CachedLicenseStatus {
  status: LicenseStatus;
  timestamp: number;
}

const LICENSE_CACHE_KEY = 'tap_license_cache';
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

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
      tap(status => {
        this.licenseStatus$.next(status);
        this.saveToCache(status);
      })
    );
  }

  /**
   * Check license status and update internal state.
   * Uses localStorage cache to provide immediate state, then refreshes
   * from the API in the background.
   */
  checkLicense(): void {
    // Load from cache immediately for instant UI state
    const cached = this.loadFromCache();
    if (cached) {
      this.licenseStatus$.next(cached);
    }

    // Always refresh from API in the background
    this.http.get<LicenseStatus>(`${this.baseUrl}/status`).subscribe({
      next: (status) => {
        this.licenseStatus$.next(status);
        this.saveToCache(status);
      },
      error: (error) => {
        // Only set inactive if we have no cached data
        if (!cached) {
          this.licenseStatus$.next({
            is_active: false,
            license_key: null,
            activated_at: null,
          });
        }
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
        this.clearCache();
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
        this.clearCache();
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

  private saveToCache(status: LicenseStatus): void {
    try {
      const cached: CachedLicenseStatus = {
        status,
        timestamp: Date.now(),
      };
      localStorage.setItem(LICENSE_CACHE_KEY, JSON.stringify(cached));
    } catch {
      // localStorage may be unavailable or full - ignore
    }
  }

  private loadFromCache(): LicenseStatus | null {
    try {
      const raw = localStorage.getItem(LICENSE_CACHE_KEY);
      if (!raw) return null;

      const cached: CachedLicenseStatus = JSON.parse(raw);
      const age = Date.now() - cached.timestamp;
      if (age > CACHE_TTL_MS) {
        localStorage.removeItem(LICENSE_CACHE_KEY);
        return null;
      }
      return cached.status;
    } catch {
      localStorage.removeItem(LICENSE_CACHE_KEY);
      return null;
    }
  }

  private clearCache(): void {
    try {
      localStorage.removeItem(LICENSE_CACHE_KEY);
    } catch {
      // ignore
    }
  }
}
