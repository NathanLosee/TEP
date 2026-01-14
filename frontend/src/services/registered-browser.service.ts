import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RegisteredBrowser {
  id: number;
  browser_uuid: string;
  browser_name: string;
  fingerprint_hash?: string;
  user_agent?: string;
  ip_address?: string;
  registered_at: string;
  last_seen: string;
  is_active: boolean;
}

export interface RegisteredBrowserCreate {
  browser_uuid: string;
  browser_name: string;
  fingerprint_hash?: string;
  user_agent?: string;
  ip_address?: string;
}

export interface BrowserVerifyRequest {
  fingerprint_hash: string;
  browser_uuid?: string;
}

export interface BrowserVerifyResponse {
  browser_uuid: string | null;
  browser_name?: string;
  verified: boolean;
  restored?: boolean;
}

export interface BrowserRecoverRequest {
  recovery_code: string;
  fingerprint_hash: string;
}

export interface BrowserRecoverResponse {
  browser_uuid: string;
  browser_name: string;
  recovered: boolean;
}

/**
 * Service for handling registered browser operations
 */
@Injectable({ providedIn: 'root' })
export class RegisteredBrowserService {
  private http = inject(HttpClient);
  private baseUrl = '/registered_browsers';

  /**
   * Register a new browser
   * @param browser The browser data to register
   * @returns The registered browser
   */
  registerBrowser(
    browser: RegisteredBrowserCreate
  ): Observable<RegisteredBrowser> {
    return this.http.post<RegisteredBrowser>(`${this.baseUrl}`, browser);
  }

  /**
   * Verify browser fingerprint and restore UUID if match found
   * @param request The verification request with fingerprint
   * @returns Verification response with UUID if match found
   */
  verifyBrowser(
    request: BrowserVerifyRequest
  ): Observable<BrowserVerifyResponse> {
    return this.http.post<BrowserVerifyResponse>(
      `${this.baseUrl}/verify`,
      request
    );
  }

  /**
   * Get all registered browsers
   * @returns An array of all registered browsers
   */
  getAllBrowsers(): Observable<RegisteredBrowser[]> {
    return this.http.get<RegisteredBrowser[]>(`${this.baseUrl}`);
  }

  /**
   * Delete a registered browser
   * @param browserId The ID of the browser to delete
   * @returns An observable indicating completion
   */
  deleteBrowser(browserId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${browserId}`);
  }

  /**
   * Recover browser registration using recovery code (UUID)
   * @param request The recovery request with code and fingerprint
   * @returns Recovery response with UUID and browser name
   */
  recoverBrowser(
    request: BrowserRecoverRequest
  ): Observable<BrowserRecoverResponse> {
    return this.http.post<BrowserRecoverResponse>(
      `${this.baseUrl}/recover`,
      request
    );
  }
}
