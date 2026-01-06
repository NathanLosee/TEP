import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RegisteredDevice {
  id: number;
  browser_uuid: string;
  browser_name: string;
}

export interface RegisteredDeviceBase {
  browser_uuid: string;
  browser_name: string;
}

/**
 * Service for handling registered browser operations
 */
@Injectable({ providedIn: 'root' })
export class RegisteredDeviceService {
  private http = inject(HttpClient);
  private baseUrl = 'registered_browsers';

  /**
   * Register a new browser
   * @param browser The browser data to register
   * @returns The registered browser
   */
  registerDevice(browser: RegisteredDeviceBase): Observable<RegisteredDevice> {
    return this.http.post<RegisteredDevice>(`${this.baseUrl}`, browser);
  }

  /**
   * Get all registered browsers
   * @returns An array of all registered browsers
   */
  getAllDevices(): Observable<RegisteredDevice[]> {
    return this.http.get<RegisteredDevice[]>(`${this.baseUrl}`);
  }

  /**
   * Delete a registered browser
   * @param browserId The ID of the browser to delete
   * @returns An observable indicating completion
   */
  deleteDevice(browserId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${browserId}`);
  }
}
