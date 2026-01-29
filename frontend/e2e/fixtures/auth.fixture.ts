import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { NavigationPage } from '../pages/navigation.page';

// Test credentials - these should match your test environment
export const TEST_CREDENTIALS = {
  admin: {
    username: '0',
    password: 'password123',
  },
};

// Extend basic test with custom fixtures
export const test = base.extend<{
  loginPage: LoginPage;
  navPage: NavigationPage;
  authenticatedPage: NavigationPage;
}>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },

  navPage: async ({ page }, use) => {
    const navPage = new NavigationPage(page);
    await use(navPage);
  },

  // Fixture that provides a page that's already logged in and at the admin dashboard
  authenticatedPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    const navPage = new NavigationPage(page);

    // Navigate to login and authenticate
    await loginPage.goto();
    await loginPage.login(TEST_CREDENTIALS.admin.username, TEST_CREDENTIALS.admin.password);

    // Wait for redirect to complete - should go to frontpage or admin
    await page.waitForLoadState('networkidle');

    // Navigate to admin area
    await navPage.gotoAdmin('dashboard');
    await navPage.expectLoggedIn();

    await use(navPage);
  },
});

export { expect };
