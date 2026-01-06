import { Injectable } from '@angular/core';

const BROWSER_UUID_KEY = 'tep_browser_uuid';
const BROWSER_NAME_KEY = 'tep_browser_name';

/**
 * Service for managing browser UUID and name in localStorage
 */
@Injectable({ providedIn: 'root' })
export class DeviceUuidService {
  /**
   * Get the current browser UUID from localStorage
   * @returns The browser UUID or null if not set
   */
  getDeviceUuid(): string | null {
    return localStorage.getItem(BROWSER_UUID_KEY);
  }

  /**
   * Get the current browser name from localStorage
   * @returns The browser name or null if not set
   */
  getBrowserName(): string | null {
    return localStorage.getItem(BROWSER_NAME_KEY);
  }

  /**
   * Save a browser UUID and name to localStorage
   * @param uuid The UUID to save
   * @param name The browser name to save
   */
  setDeviceUuid(uuid: string, name?: string): void {
    localStorage.setItem(BROWSER_UUID_KEY, uuid);
    if (name) {
      localStorage.setItem(BROWSER_NAME_KEY, name);
    }
  }

  /**
   * Clear the browser UUID and name from localStorage
   */
  clearDeviceUuid(): void {
    localStorage.removeItem(BROWSER_UUID_KEY);
    localStorage.removeItem(BROWSER_NAME_KEY);
  }

  /**
   * Check if a browser UUID is currently stored
   * @returns True if a UUID exists in localStorage
   */
  hasDeviceUuid(): boolean {
    return this.getDeviceUuid() !== null;
  }
}
