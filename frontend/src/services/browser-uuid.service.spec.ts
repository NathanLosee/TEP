import { TestBed } from '@angular/core/testing';
import { BrowserUuidService } from './browser-uuid.service';

describe('BrowserUuidService', () => {
  let service: BrowserUuidService;
  const BROWSER_UUID_KEY = 'tep_browser_uuid';
  const BROWSER_NAME_KEY = 'tep_browser_name';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [BrowserUuidService]
    });
    service = TestBed.inject(BrowserUuidService);

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getBrowserUuid', () => {
    it('should return null when no UUID is stored', () => {
      expect(service.getBrowserUuid()).toBeNull();
    });

    it('should return the stored UUID', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';
      localStorage.setItem(BROWSER_UUID_KEY, uuid);

      expect(service.getBrowserUuid()).toBe(uuid);
    });

    it('should return the exact UUID string stored', () => {
      const uuid = 'custom-uuid-format';
      localStorage.setItem(BROWSER_UUID_KEY, uuid);

      expect(service.getBrowserUuid()).toBe(uuid);
    });
  });

  describe('getBrowserName', () => {
    it('should return null when no browser name is stored', () => {
      expect(service.getBrowserName()).toBeNull();
    });

    it('should return the stored browser name', () => {
      const browserName = 'Chrome on Desktop';
      localStorage.setItem(BROWSER_NAME_KEY, browserName);

      expect(service.getBrowserName()).toBe(browserName);
    });

    it('should handle browser names with special characters', () => {
      const browserName = 'Firefox - John\'s Laptop (2024)';
      localStorage.setItem(BROWSER_NAME_KEY, browserName);

      expect(service.getBrowserName()).toBe(browserName);
    });
  });

  describe('setBrowserUuid', () => {
    it('should store UUID in localStorage', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      service.setBrowserUuid(uuid);

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
    });

    it('should store both UUID and browser name when name is provided', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';
      const name = 'Chrome on Desktop';

      service.setBrowserUuid(uuid, name);

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBe(name);
    });

    it('should only store UUID when name is not provided', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      service.setBrowserUuid(uuid);

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should only store UUID when name is empty string', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      service.setBrowserUuid(uuid, '');

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should update existing UUID', () => {
      const oldUuid = 'old-uuid';
      const newUuid = 'new-uuid';

      service.setBrowserUuid(oldUuid);
      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(oldUuid);

      service.setBrowserUuid(newUuid);
      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(newUuid);
    });

    it('should update both UUID and name when both change', () => {
      service.setBrowserUuid('old-uuid', 'Old Name');
      service.setBrowserUuid('new-uuid', 'New Name');

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe('new-uuid');
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBe('New Name');
    });
  });

  describe('clearBrowserUuid', () => {
    it('should remove UUID from localStorage', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      service.clearBrowserUuid();

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBeNull();
    });

    it('should remove browser name from localStorage', () => {
      localStorage.setItem(BROWSER_NAME_KEY, 'Test Browser');

      service.clearBrowserUuid();

      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should remove both UUID and browser name', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');
      localStorage.setItem(BROWSER_NAME_KEY, 'Test Browser');

      service.clearBrowserUuid();

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBeNull();
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should not throw error when clearing non-existent data', () => {
      expect(() => service.clearBrowserUuid()).not.toThrow();
    });

    it('should not affect other localStorage data', () => {
      localStorage.setItem('other_key', 'other_value');
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      service.clearBrowserUuid();

      expect(localStorage.getItem('other_key')).toBe('other_value');
    });
  });

  describe('hasBrowserUuid', () => {
    it('should return false when no UUID is stored', () => {
      expect(service.hasBrowserUuid()).toBe(false);
    });

    it('should return true when UUID is stored', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      expect(service.hasBrowserUuid()).toBe(true);
    });

    it('should return false after UUID is cleared', () => {
      service.setBrowserUuid('test-uuid');
      expect(service.hasBrowserUuid()).toBe(true);

      service.clearBrowserUuid();
      expect(service.hasBrowserUuid()).toBe(false);
    });

    it('should return true even if browser name is not set', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      expect(service.hasBrowserUuid()).toBe(true);
      expect(service.getBrowserName()).toBeNull();
    });
  });

  describe('integration scenarios', () => {
    it('should handle full device registration lifecycle', () => {
      // Initial state - no device registered
      expect(service.hasBrowserUuid()).toBe(false);
      expect(service.getBrowserUuid()).toBeNull();
      expect(service.getBrowserName()).toBeNull();

      // Register device
      const uuid = '123e4567-e89b-12d3-a456-426614174000';
      const name = 'Chrome on Windows';
      service.setBrowserUuid(uuid, name);

      expect(service.hasBrowserUuid()).toBe(true);
      expect(service.getBrowserUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBe(name);

      // Clear device
      service.clearBrowserUuid();

      expect(service.hasBrowserUuid()).toBe(false);
      expect(service.getBrowserUuid()).toBeNull();
      expect(service.getBrowserName()).toBeNull();
    });

    it('should handle device name update without UUID change', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      // Initial registration
      service.setBrowserUuid(uuid, 'Initial Name');
      expect(service.getBrowserName()).toBe('Initial Name');

      // Update name only
      service.setBrowserUuid(uuid, 'Updated Name');
      expect(service.getBrowserUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBe('Updated Name');
    });

    it('should handle registration without name, then adding name later', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      // Register without name
      service.setBrowserUuid(uuid);
      expect(service.getBrowserUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBeNull();

      // Add name later
      service.setBrowserUuid(uuid, 'Added Name');
      expect(service.getBrowserUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBe('Added Name');
    });

    it('should handle multiple device switches', () => {
      // Device 1
      service.setBrowserUuid('uuid-1', 'Device 1');
      expect(service.getBrowserUuid()).toBe('uuid-1');
      expect(service.getBrowserName()).toBe('Device 1');

      // Device 2
      service.setBrowserUuid('uuid-2', 'Device 2');
      expect(service.getBrowserUuid()).toBe('uuid-2');
      expect(service.getBrowserName()).toBe('Device 2');

      // Back to Device 1
      service.setBrowserUuid('uuid-1', 'Device 1');
      expect(service.getBrowserUuid()).toBe('uuid-1');
      expect(service.getBrowserName()).toBe('Device 1');
    });

    it('should handle edge case with empty UUID', () => {
      service.setBrowserUuid('', 'Empty UUID Test');

      expect(service.getBrowserUuid()).toBe('');
      expect(service.hasBrowserUuid()).toBe(true); // localStorage stores empty string
      expect(service.getBrowserName()).toBe('Empty UUID Test');
    });
  });

  describe('persistence', () => {
    it('should persist UUID across service instances', () => {
      const uuid = 'persistent-uuid';
      service.setBrowserUuid(uuid, 'Test');

      // Create new service instance
      const newService = TestBed.inject(BrowserUuidService);

      expect(newService.getBrowserUuid()).toBe(uuid);
      expect(newService.getBrowserName()).toBe('Test');
    });
  });
});
