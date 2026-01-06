import { Component, DebugElement } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { HasPermissionDirective, DisableIfNoPermissionDirective } from './has-permission.directive';
import { PermissionService, UserPermissions } from '../../services/permission.service';

// Test component for structural directive
@Component({
  standalone: true,
  imports: [HasPermissionDirective],
  template: `
    <div *hasPermission="permission" id="content">Content</div>
  `
})
class TestHasPermissionComponent {
  permission: string | string[] = 'user.read';
}

// Test component for structural directive with requireAll
@Component({
  standalone: true,
  imports: [HasPermissionDirective],
  template: `
    <div *hasPermission="permissions; requireAll: requireAll" id="content">Content</div>
  `
})
class TestHasPermissionRequireAllComponent {
  permissions: string[] = ['user.read', 'user.write'];
  requireAll = false;
}

// Test component for attribute directive
@Component({
  standalone: true,
  imports: [DisableIfNoPermissionDirective],
  template: `
    <button [disableIfNoPermission]="permission" id="test-button">Click Me</button>
  `
})
class TestDisableIfNoPermissionComponent {
  permission: string | string[] = 'user.write';
}

// Test component for attribute directive with requireAll
@Component({
  standalone: true,
  imports: [DisableIfNoPermissionDirective],
  template: `
    <button [disableIfNoPermission]="permissions" [disableIfNoPermissionRequireAll]="requireAll" id="test-button">
      Click Me
    </button>
  `
})
class TestDisableIfNoPermissionRequireAllComponent {
  permissions: string[] = ['user.write', 'user.delete'];
  requireAll = false;
}

describe('HasPermissionDirective', () => {
  let permissionService: PermissionService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [TestHasPermissionComponent, TestHasPermissionRequireAllComponent],
      providers: [PermissionService]
    });

    permissionService = TestBed.inject(PermissionService);
  });

  describe('single permission', () => {
    let fixture: ComponentFixture<TestHasPermissionComponent>;
    let component: TestHasPermissionComponent;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestHasPermissionComponent);
      component = fixture.componentInstance;
    });

    it('should show content when user has permission', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'user.write'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permission = 'user.read';
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeTruthy();
      expect(contentElement.nativeElement.textContent).toContain('Content');
    });

    it('should hide content when user does not have permission', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permission = 'user.delete';
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeNull();
    });

    it('should hide content when no permissions are set', () => {
      component.permission = 'user.read';
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeNull();
    });

    it('should react to permission changes', () => {
      component.permission = 'user.write';
      fixture.detectChanges();

      // Initially no permissions
      let contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeNull();

      // Grant permissions
      permissionService.setPermissions({ scopes: ['user.write'], badge_number: 'EMP001' });
      fixture.detectChanges();

      contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeTruthy();

      // Revoke permissions
      permissionService.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      fixture.detectChanges();

      contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeNull();
    });
  });

  describe('multiple permissions with hasAnyPermission mode', () => {
    let fixture: ComponentFixture<TestHasPermissionRequireAllComponent>;
    let component: TestHasPermissionRequireAllComponent;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestHasPermissionRequireAllComponent);
      component = fixture.componentInstance;
    });

    it('should show content when user has any of the permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.read', 'user.write'];
      component.requireAll = false;
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeTruthy();
    });

    it('should hide content when user has none of the permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['employee.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.read', 'user.write'];
      component.requireAll = false;
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeNull();
    });
  });

  describe('multiple permissions with requireAll mode', () => {
    let fixture: ComponentFixture<TestHasPermissionRequireAllComponent>;
    let component: TestHasPermissionRequireAllComponent;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestHasPermissionRequireAllComponent);
      component = fixture.componentInstance;
    });

    it('should show content when user has all permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read', 'user.write', 'employee.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.read', 'user.write'];
      component.requireAll = true;
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeTruthy();
    });

    it('should hide content when user is missing any permission', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.read', 'user.write'];
      component.requireAll = true;
      fixture.detectChanges();

      const contentElement = fixture.debugElement.query(By.css('#content'));
      expect(contentElement).toBeNull();
    });
  });
});

describe('DisableIfNoPermissionDirective', () => {
  let permissionService: PermissionService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        TestDisableIfNoPermissionComponent,
        TestDisableIfNoPermissionRequireAllComponent
      ],
      providers: [PermissionService]
    });

    permissionService = TestBed.inject(PermissionService);
  });

  describe('single permission', () => {
    let fixture: ComponentFixture<TestDisableIfNoPermissionComponent>;
    let component: TestDisableIfNoPermissionComponent;
    let buttonElement: DebugElement;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestDisableIfNoPermissionComponent);
      component = fixture.componentInstance;
      buttonElement = fixture.debugElement.query(By.css('#test-button'));
    });

    it('should not disable button when user has permission', () => {
      const permissions: UserPermissions = {
        scopes: ['user.write'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permission = 'user.write';
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(false);
      expect(buttonElement.nativeElement.classList.contains('permission-disabled')).toBe(false);
    });

    it('should disable button when user does not have permission', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permission = 'user.write';
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(true);
      expect(buttonElement.nativeElement.classList.contains('permission-disabled')).toBe(true);
      expect(buttonElement.nativeElement.style.opacity).toBe('0.5');
      expect(buttonElement.nativeElement.style.cursor).toBe('not-allowed');
      expect(buttonElement.nativeElement.style.pointerEvents).toBe('none');
    });

    it('should not disable button when permissions have not loaded yet', () => {
      component.permission = 'user.write';
      fixture.detectChanges();

      // When permissions are null (not yet loaded), don't disable
      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(false);
    });

    it('should react to permission changes', () => {
      component.permission = 'user.delete';

      // Set initial permissions without user.delete
      permissionService.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(true);

      // Grant user.delete permission
      permissionService.setPermissions({
        scopes: ['user.read', 'user.delete'],
        badge_number: 'EMP001'
      });
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(false);
      expect(buttonElement.nativeElement.classList.contains('permission-disabled')).toBe(false);

      // Revoke permission
      permissionService.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(true);
    });
  });

  describe('multiple permissions with hasAnyPermission mode', () => {
    let fixture: ComponentFixture<TestDisableIfNoPermissionRequireAllComponent>;
    let component: TestDisableIfNoPermissionRequireAllComponent;
    let buttonElement: DebugElement;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestDisableIfNoPermissionRequireAllComponent);
      component = fixture.componentInstance;
      buttonElement = fixture.debugElement.query(By.css('#test-button'));
    });

    it('should not disable when user has any of the permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.write'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.write', 'user.delete'];
      component.requireAll = false;
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(false);
    });

    it('should disable when user has none of the permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.write', 'user.delete'];
      component.requireAll = false;
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(true);
    });
  });

  describe('multiple permissions with requireAll mode', () => {
    let fixture: ComponentFixture<TestDisableIfNoPermissionRequireAllComponent>;
    let component: TestDisableIfNoPermissionRequireAllComponent;
    let buttonElement: DebugElement;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestDisableIfNoPermissionRequireAllComponent);
      component = fixture.componentInstance;
      buttonElement = fixture.debugElement.query(By.css('#test-button'));
    });

    it('should not disable when user has all permissions', () => {
      const permissions: UserPermissions = {
        scopes: ['user.write', 'user.delete', 'employee.read'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.write', 'user.delete'];
      component.requireAll = true;
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(false);
    });

    it('should disable when user is missing any permission', () => {
      const permissions: UserPermissions = {
        scopes: ['user.write'],
        badge_number: 'EMP001'
      };
      permissionService.setPermissions(permissions);

      component.permissions = ['user.write', 'user.delete'];
      component.requireAll = true;
      fixture.detectChanges();

      expect(buttonElement.nativeElement.hasAttribute('disabled')).toBe(true);
    });
  });

  describe('styling', () => {
    let fixture: ComponentFixture<TestDisableIfNoPermissionComponent>;
    let buttonElement: DebugElement;

    beforeEach(() => {
      fixture = TestBed.createComponent(TestDisableIfNoPermissionComponent);
      buttonElement = fixture.debugElement.query(By.css('#test-button'));
    });

    it('should apply disabled styling when permission is missing', () => {
      permissionService.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      fixture.componentInstance.permission = 'user.write';
      fixture.detectChanges();

      const element = buttonElement.nativeElement;
      expect(element.style.opacity).toBe('0.5');
      expect(element.style.cursor).toBe('not-allowed');
      expect(element.style.pointerEvents).toBe('none');
      expect(element.classList.contains('permission-disabled')).toBe(true);
    });

    it('should remove disabled styling when permission is granted', () => {
      // Initially no permission
      permissionService.setPermissions({ scopes: ['user.read'], badge_number: 'EMP001' });
      fixture.componentInstance.permission = 'user.write';
      fixture.detectChanges();

      expect(buttonElement.nativeElement.style.opacity).toBe('0.5');

      // Grant permission
      permissionService.setPermissions({
        scopes: ['user.read', 'user.write'],
        badge_number: 'EMP001'
      });
      fixture.detectChanges();

      const element = buttonElement.nativeElement;
      expect(element.style.opacity).toBe('');
      expect(element.style.cursor).toBe('');
      expect(element.style.pointerEvents).toBe('');
      expect(element.classList.contains('permission-disabled')).toBe(false);
    });
  });
});
