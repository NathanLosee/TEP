import { test, expect } from './fixtures/auth.fixture';

test.describe('Navigation', () => {
  test.describe('Admin Dashboard', () => {
    test('should display admin dashboard', async ({ authenticatedPage, page }) => {
      await expect(page).toHaveURL(/\/admin\/dashboard/);
    });

    test('should display navigation menu when logged in', async ({ authenticatedPage, page }) => {
      // Check that main navigation elements are visible
      await expect(page.locator('mat-sidenav, mat-nav-list').first()).toBeVisible();
    });
  });

  test.describe('Side Navigation Links', () => {
    test('should navigate to Employees page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('employees');
      await expect(page).toHaveURL(/\/admin\/employees/);
    });

    test('should navigate to Timeclock Entries page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('timeclock-entries');
      await expect(page).toHaveURL(/\/admin\/timeclock-entries/);
    });

    test('should navigate to Departments page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('departments');
      await expect(page).toHaveURL(/\/admin\/departments/);
    });

    test('should navigate to Org Units page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('org-units');
      await expect(page).toHaveURL(/\/admin\/org-units/);
    });

    test('should navigate to Holiday Groups page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('holiday-groups');
      await expect(page).toHaveURL(/\/admin\/holiday-groups/);
    });

    test('should navigate to Users page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('users');
      await expect(page).toHaveURL(/\/admin\/users/);
    });

    test('should navigate to Auth Roles page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('auth-roles');
      await expect(page).toHaveURL(/\/admin\/auth-roles/);
    });

    test('should navigate to Registered Browsers page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('registered-browsers');
      await expect(page).toHaveURL(/\/admin\/registered-browsers/);
    });

    test('should navigate to Reports page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('reports');
      await expect(page).toHaveURL(/\/admin\/reports/);
    });

    test('should navigate to Event Logs page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('event-logs');
      await expect(page).toHaveURL(/\/admin\/event-logs/);
    });

    test('should navigate to License page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('license');
      await expect(page).toHaveURL(/\/admin\/license/);
    });

    test('should navigate to System Settings page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.navigateTo('settings');
      await expect(page).toHaveURL(/\/admin\/settings/);
    });
  });

  test.describe('Responsive Navigation', () => {
    test('should work on mobile viewport', async ({ authenticatedPage, page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Navigation should still be accessible (might be in a hamburger menu)
      const menuButton = page.locator('button:has(mat-icon:has-text("menu"))');
      const menuVisible = await menuButton.isVisible().catch(() => false);

      if (menuVisible) {
        await menuButton.click();
        await page.waitForTimeout(300); // Wait for animation
      }

      // Should be able to see navigation content
      await expect(page.locator('mat-sidenav, mat-nav-list').first()).toBeVisible();
    });
  });
});
