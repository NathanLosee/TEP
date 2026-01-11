import { Injectable } from '@angular/core';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

const BROWSER_UUID_KEY = 'tep_browser_uuid';
const BROWSER_NAME_KEY = 'tep_browser_name';
const SESSION_UUID_KEY = 'tep_session_uuid'; // For duplicate detection

/**
 * Service for managing browser UUID, name, and fingerprint
 */
@Injectable({ providedIn: 'root' })
export class DeviceUuidService {
  private fpPromise = FingerprintJS.load();

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
   * Get the session UUID from sessionStorage (used for duplicate detection)
   * @returns The session UUID or null if not set
   */
  getSessionUuid(): string | null {
    return sessionStorage.getItem(SESSION_UUID_KEY);
  }

  /**
   * Save a browser UUID and name to localStorage and sessionStorage
   * @param uuid The UUID to save
   * @param name The browser name to save
   */
  setDeviceUuid(uuid: string, name?: string): void {
    // Store in localStorage for persistence
    localStorage.setItem(BROWSER_UUID_KEY, uuid);
    if (name) {
      localStorage.setItem(BROWSER_NAME_KEY, name);
    }

    // Also store in sessionStorage for duplicate detection
    sessionStorage.setItem(SESSION_UUID_KEY, uuid);
  }

  /**
   * Clear the browser UUID and name from localStorage and sessionStorage
   */
  clearDeviceUuid(): void {
    localStorage.removeItem(BROWSER_UUID_KEY);
    localStorage.removeItem(BROWSER_NAME_KEY);
    sessionStorage.removeItem(SESSION_UUID_KEY);
  }

  /**
   * Check if the current UUID conflicts with an active session
   * @param uuid The UUID to check
   * @returns True if this UUID is already in use in another session
   */
  isUuidInActiveSession(uuid: string): boolean {
    const sessionUuid = this.getSessionUuid();
    // If there's a session UUID and it doesn't match, there's a conflict
    return sessionUuid !== null && sessionUuid !== uuid;
  }

  /**
   * Check if a browser UUID is currently stored
   * @returns True if a UUID exists in localStorage
   */
  hasDeviceUuid(): boolean {
    return this.getDeviceUuid() !== null;
  }

  /**
   * Generate a browser fingerprint hash
   * @returns A promise that resolves to the fingerprint hash
   */
  async generateFingerprint(): Promise<string> {
    const fp = await this.fpPromise;
    const result = await fp.get();
    return result.visitorId;
  }
}
