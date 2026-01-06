import { TestBed } from '@angular/core/testing';
import { DeviceUuidService } from './device-uuid.service';

describe('DeviceUuidService', () => {
  let service: DeviceUuidService;
  const BROWSER_UUID_KEY = 'tep_browser_uuid';
  const BROWSER_NAME_KEY = 'tep_browser_name';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [DeviceUuidService]
    });
    service = TestBed.inject(DeviceUuidService);

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getDeviceUuid', () => {
    it('should return null when no UUID is stored', () => {
      expect(service.getDeviceUuid()).toBeNull();
    });

    it('should return the stored UUID', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';
      localStorage.setItem(BROWSER_UUID_KEY, uuid);

      expect(service.getDeviceUuid()).toBe(uuid);
    });

    it('should return the exact UUID string stored', () => {
      const uuid = 'custom-uuid-format';
      localStorage.setItem(BROWSER_UUID_KEY, uuid);

      expect(service.getDeviceUuid()).toBe(uuid);
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

  describe('setDeviceUuid', () => {
    it('should store UUID in localStorage', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      service.setDeviceUuid(uuid);

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
    });

    it('should store both UUID and browser name when name is provided', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';
      const name = 'Chrome on Desktop';

      service.setDeviceUuid(uuid, name);

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBe(name);
    });

    it('should only store UUID when name is not provided', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      service.setDeviceUuid(uuid);

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should only store UUID when name is empty string', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      service.setDeviceUuid(uuid, '');

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(uuid);
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should update existing UUID', () => {
      const oldUuid = 'old-uuid';
      const newUuid = 'new-uuid';

      service.setDeviceUuid(oldUuid);
      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(oldUuid);

      service.setDeviceUuid(newUuid);
      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe(newUuid);
    });

    it('should update both UUID and name when both change', () => {
      service.setDeviceUuid('old-uuid', 'Old Name');
      service.setDeviceUuid('new-uuid', 'New Name');

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBe('new-uuid');
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBe('New Name');
    });
  });

  describe('clearDeviceUuid', () => {
    it('should remove UUID from localStorage', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      service.clearDeviceUuid();

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBeNull();
    });

    it('should remove browser name from localStorage', () => {
      localStorage.setItem(BROWSER_NAME_KEY, 'Test Browser');

      service.clearDeviceUuid();

      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should remove both UUID and browser name', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');
      localStorage.setItem(BROWSER_NAME_KEY, 'Test Browser');

      service.clearDeviceUuid();

      expect(localStorage.getItem(BROWSER_UUID_KEY)).toBeNull();
      expect(localStorage.getItem(BROWSER_NAME_KEY)).toBeNull();
    });

    it('should not throw error when clearing non-existent data', () => {
      expect(() => service.clearDeviceUuid()).not.toThrow();
    });

    it('should not affect other localStorage data', () => {
      localStorage.setItem('other_key', 'other_value');
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      service.clearDeviceUuid();

      expect(localStorage.getItem('other_key')).toBe('other_value');
    });
  });

  describe('hasDeviceUuid', () => {
    it('should return false when no UUID is stored', () => {
      expect(service.hasDeviceUuid()).toBe(false);
    });

    it('should return true when UUID is stored', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      expect(service.hasDeviceUuid()).toBe(true);
    });

    it('should return false after UUID is cleared', () => {
      service.setDeviceUuid('test-uuid');
      expect(service.hasDeviceUuid()).toBe(true);

      service.clearDeviceUuid();
      expect(service.hasDeviceUuid()).toBe(false);
    });

    it('should return true even if browser name is not set', () => {
      localStorage.setItem(BROWSER_UUID_KEY, 'test-uuid');

      expect(service.hasDeviceUuid()).toBe(true);
      expect(service.getBrowserName()).toBeNull();
    });
  });

  describe('integration scenarios', () => {
    it('should handle full device registration lifecycle', () => {
      // Initial state - no device registered
      expect(service.hasDeviceUuid()).toBe(false);
      expect(service.getDeviceUuid()).toBeNull();
      expect(service.getBrowserName()).toBeNull();

      // Register device
      const uuid = '123e4567-e89b-12d3-a456-426614174000';
      const name = 'Chrome on Windows';
      service.setDeviceUuid(uuid, name);

      expect(service.hasDeviceUuid()).toBe(true);
      expect(service.getDeviceUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBe(name);

      // Clear device
      service.clearDeviceUuid();

      expect(service.hasDeviceUuid()).toBe(false);
      expect(service.getDeviceUuid()).toBeNull();
      expect(service.getBrowserName()).toBeNull();
    });

    it('should handle device name update without UUID change', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      // Initial registration
      service.setDeviceUuid(uuid, 'Initial Name');
      expect(service.getBrowserName()).toBe('Initial Name');

      // Update name only
      service.setDeviceUuid(uuid, 'Updated Name');
      expect(service.getDeviceUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBe('Updated Name');
    });

    it('should handle registration without name, then adding name later', () => {
      const uuid = '123e4567-e89b-12d3-a456-426614174000';

      // Register without name
      service.setDeviceUuid(uuid);
      expect(service.getDeviceUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBeNull();

      // Add name later
      service.setDeviceUuid(uuid, 'Added Name');
      expect(service.getDeviceUuid()).toBe(uuid);
      expect(service.getBrowserName()).toBe('Added Name');
    });

    it('should handle multiple device switches', () => {
      // Device 1
      service.setDeviceUuid('uuid-1', 'Device 1');
      expect(service.getDeviceUuid()).toBe('uuid-1');
      expect(service.getBrowserName()).toBe('Device 1');

      // Device 2
      service.setDeviceUuid('uuid-2', 'Device 2');
      expect(service.getDeviceUuid()).toBe('uuid-2');
      expect(service.getBrowserName()).toBe('Device 2');

      // Back to Device 1
      service.setDeviceUuid('uuid-1', 'Device 1');
      expect(service.getDeviceUuid()).toBe('uuid-1');
      expect(service.getBrowserName()).toBe('Device 1');
    });

    it('should handle edge case with empty UUID', () => {
      service.setDeviceUuid('', 'Empty UUID Test');

      expect(service.getDeviceUuid()).toBe('');
      expect(service.hasDeviceUuid()).toBe(true); // localStorage stores empty string
      expect(service.getBrowserName()).toBe('Empty UUID Test');
    });
  });

  describe('persistence', () => {
    it('should persist UUID across service instances', () => {
      const uuid = 'persistent-uuid';
      service.setDeviceUuid(uuid, 'Test');

      // Create new service instance
      const newService = TestBed.inject(DeviceUuidService);

      expect(newService.getDeviceUuid()).toBe(uuid);
      expect(newService.getBrowserName()).toBe('Test');
    });
  });
});
