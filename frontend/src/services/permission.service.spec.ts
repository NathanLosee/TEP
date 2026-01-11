import { TestBed } from '@angular/core/testing';
import { PermissionService, UserPermissions } from './permission.service';
import { take } from 'rxjs/operators';

describe('PermissionService', () => {
  let service: PermissionService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PermissionService]
    });
    service = TestBed.inject(PermissionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('setPermissions', () => {
    it('should set user permissions', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'user.write', 'employee.read'],
        badge_number: 'EMP001'
      };

      service.permissions$.pipe(take(2)).subscribe(perms => {
        if (perms !== null) {
          expect(perms).toEqual(permissions);
          done();
        }
      });

      service.setPermissions(permissions);
    });

    it('should update existing permissions', () => {
      const oldPermissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      const newPermissions: UserPermissions = {
        scopes: ['user.read', 'user.write'],
        badge_number: 'EMP002'
      };

      service.setPermissions(oldPermissions);
      expect(service.getCurrentPermissions()).toEqual(oldPermissions);

      service.setPermissions(newPermissions);
      expect(service.getCurrentPermissions()).toEqual(newPermissions);
    });
  });

  describe('getCurrentPermissions', () => {
    it('should return null when no permissions are set', () => {
      expect(service.getCurrentPermissions()).toBeNull();
    });

    it('should return current permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);
      expect(service.getCurrentPermissions()).toEqual(permissions);
    });
  });

  describe('clearPermissions', () => {
    it('should clear user permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);
      expect(service.getCurrentPermissions()).not.toBeNull();

      service.clearPermissions();
      expect(service.getCurrentPermissions()).toBeNull();
    });

    it('should emit null through permissions$ observable', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      // Subscribe first, then clear - this way we catch the next emission
      service.permissions$.pipe(take(2)).subscribe(perms => {
        // First emission is current value (permissions), second is null after clear
        if (perms === null) {
          expect(perms).toBeNull();
          done();
        }
      });

      service.clearPermissions();
    });
  });

  describe('hasPermission', () => {
    beforeEach(() => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'user.write', 'employee.read', 'department.delete'],
        badge_number: 'EMP001'
      };
      service.setPermissions(permissions);
    });

    it('should return true for existing permission', () => {
      expect(service.hasPermission('user.read')).toBe(true);
      expect(service.hasPermission('employee.read')).toBe(true);
    });

    it('should return false for non-existing permission', () => {
      expect(service.hasPermission('user.delete')).toBe(false);
      expect(service.hasPermission('nonexistent.permission')).toBe(false);
    });

    it('should return false when no permissions are set', () => {
      service.clearPermissions();
      expect(service.hasPermission('user.read')).toBe(false);
    });

    it('should be case-sensitive', () => {
      expect(service.hasPermission('user.read')).toBe(true);
      expect(service.hasPermission('USER.READ')).toBe(false);
    });
  });

  describe('hasAnyPermission', () => {
    beforeEach(() => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'employee.read', 'department.write'],
        badge_number: 'EMP001'
      };
      service.setPermissions(permissions);
    });

    it('should return true if user has any of the required permissions', () => {
      expect(service.hasAnyPermission(['user.read', 'user.write'])).toBe(true);
      expect(service.hasAnyPermission(['employee.read', 'employee.write'])).toBe(true);
    });

    it('should return false if user has none of the required permissions', () => {
      expect(service.hasAnyPermission(['user.delete', 'employee.delete'])).toBe(false);
    });

    it('should return false for empty permission array', () => {
      expect(service.hasAnyPermission([])).toBe(false);
    });

    it('should return false when no permissions are set', () => {
      service.clearPermissions();
      expect(service.hasAnyPermission(['user.read', 'user.write'])).toBe(false);
    });
  });

  describe('hasAllPermissions', () => {
    beforeEach(() => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'user.write', 'employee.read'],
        badge_number: 'EMP001'
      };
      service.setPermissions(permissions);
    });

    it('should return true if user has all required permissions', () => {
      expect(service.hasAllPermissions(['user.read', 'employee.read'])).toBe(true);
      expect(service.hasAllPermissions(['user.read'])).toBe(true);
    });

    it('should return false if user is missing any required permission', () => {
      expect(service.hasAllPermissions(['user.read', 'user.delete'])).toBe(false);
      expect(service.hasAllPermissions(['employee.read', 'employee.write'])).toBe(false);
    });

    it('should return true for empty permission array', () => {
      expect(service.hasAllPermissions([])).toBe(true);
    });

    it('should return false when no permissions are set', () => {
      service.clearPermissions();
      expect(service.hasAllPermissions(['user.read'])).toBe(false);
    });
  });

  describe('hasPermission$ observable', () => {
    it('should emit true when user has permission', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      service.hasPermission$('user.read').pipe(take(1)).subscribe(hasPermission => {
        expect(hasPermission).toBe(true);
        done();
      });
    });

    it('should emit false when user does not have permission', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      service.hasPermission$('user.write').pipe(take(1)).subscribe(hasPermission => {
        expect(hasPermission).toBe(false);
        done();
      });
    });

    it('should react to permission changes', (done) => {
      let emissionCount = 0;
      // BehaviorSubject emits current value (null) first, then emissions from setPermissions
      // Emissions: null→false, {user.read}→false, {user.read,user.write}→true
      const expected = [false, false, true];

      service.hasPermission$('user.write').pipe(take(3)).subscribe(hasPermission => {
        expect(hasPermission).toBe(expected[emissionCount]);
        emissionCount++;
        if (emissionCount === 3) done();
      });

      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      service.setPermissions({ scopes: ['user.read', 'user.write'], badge_number: 'EMP001' });
    });
  });

  describe('hasAnyPermission$ observable', () => {
    it('should emit true when user has any permission', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      service.hasAnyPermission$(['user.read', 'user.write']).pipe(take(1)).subscribe(hasPermission => {
        expect(hasPermission).toBe(true);
        done();
      });
    });

    it('should emit false when user has none of the permissions', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      service.hasAnyPermission$(['user.write', 'user.delete']).pipe(take(1)).subscribe(hasPermission => {
        expect(hasPermission).toBe(false);
        done();
      });
    });
  });

  describe('hasAllPermissions$ observable', () => {
    it('should emit true when user has all permissions', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'user.write'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      service.hasAllPermissions$(['user.read', 'user.write']).pipe(take(1)).subscribe(hasPermission => {
        expect(hasPermission).toBe(true);
        done();
      });
    });

    it('should emit false when user is missing any permission', (done) => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);

      service.hasAllPermissions$(['user.read', 'user.write']).pipe(take(1)).subscribe(hasPermission => {
        expect(hasPermission).toBe(false);
        done();
      });
    });
  });

  describe('getBadgeNumber', () => {
    it('should return null when no permissions are set', () => {
      expect(service.getBadgeNumber()).toBeNull();
    });

    it('should return user badge number', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);
      expect(service.getBadgeNumber()).toBe('EMP001');
    });

    it('should return updated badge number when permissions change', () => {
      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      expect(service.getBadgeNumber()).toBe('EMP001');

      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP002' });
      expect(service.getBadgeNumber()).toBe('EMP002');
    });
  });

  describe('isLoggedIn', () => {
    it('should return false when no permissions are set', () => {
      expect(service.isLoggedIn()).toBe(false);
    });

    it('should return true when permissions are set', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };

      service.setPermissions(permissions);
      expect(service.isLoggedIn()).toBe(true);
    });

    it('should return false after clearPermissions', () => {
      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      expect(service.isLoggedIn()).toBe(true);

      service.clearPermissions();
      expect(service.isLoggedIn()).toBe(false);
    });
  });

  describe('isLoggedIn$ observable', () => {
    it('should emit false when no permissions are set', (done) => {
      service.isLoggedIn$().pipe(take(1)).subscribe(isLoggedIn => {
        expect(isLoggedIn).toBe(false);
        done();
      });
    });

    it('should emit true when permissions are set', (done) => {
      service.permissions$.pipe(take(2)).subscribe(perms => {
        if (perms !== null) {
          service.isLoggedIn$().pipe(take(1)).subscribe(isLoggedIn => {
            expect(isLoggedIn).toBe(true);
            done();
          });
        }
      });

      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
    });

    it('should react to login/logout changes', (done) => {
      let emissionCount = 0;
      const expected = [false, true, false];

      service.isLoggedIn$().pipe(take(3)).subscribe(isLoggedIn => {
        expect(isLoggedIn).toBe(expected[emissionCount]);
        emissionCount++;
        if (emissionCount === 3) done();
      });

      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      service.clearPermissions();
    });
  });

  describe('integration scenarios', () => {
    it('should handle full authentication lifecycle', () => {
      // Initial state - not logged in
      expect(service.isLoggedIn()).toBe(false);
      expect(service.getCurrentPermissions()).toBeNull();

      // Login
      const loginPermissions: UserPermissions = {
        scopes: ['user.read', 'user.write', 'employee.read'],
        badge_number: 'EMP001'
      };
      service.setPermissions(loginPermissions);

      expect(service.isLoggedIn()).toBe(true);
      expect(service.getBadgeNumber()).toBe('EMP001');
      expect(service.hasPermission('user.read')).toBe(true);
      expect(service.hasAllPermissions(['user.read', 'employee.read'])).toBe(true);

      // Logout
      service.clearPermissions();

      expect(service.isLoggedIn()).toBe(false);
      expect(service.getBadgeNumber()).toBeNull();
      expect(service.hasPermission('user.read')).toBe(false);
    });

    it('should handle admin-like permission set', () => {
      const adminPermissions: UserPermissions = {
        scopes: [
          'user.read', 'user.write', 'user.delete',
          'employee.read', 'employee.write', 'employee.delete',
          'department.read', 'department.write', 'department.delete'
        ],
        badge_number: 'ADMIN001'
      };

      service.setPermissions(adminPermissions);

      expect(service.hasAllPermissions(['user.read', 'user.write', 'user.delete'])).toBe(true);
      expect(service.hasAnyPermission(['user.delete', 'nonexistent.permission'])).toBe(true);
      expect(service.getBadgeNumber()).toBe('ADMIN001');
    });

    it('should handle permission updates mid-session', () => {
      // Initial login with limited permissions
      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      expect(service.hasPermission('user.write')).toBe(false);

      // Permissions upgraded
      service.setPermissions({ scopes: ['user.read', 'user.write'], badge_number: 'EMP001' });
      expect(service.hasPermission('user.write')).toBe(true);

      // Permissions downgraded
      service.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      expect(service.hasPermission('user.write')).toBe(false);
    });
  });
});
