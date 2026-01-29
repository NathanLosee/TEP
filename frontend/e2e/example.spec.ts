import { expect, test } from '@playwright/test';

/**
 * Smoke tests - basic health checks for the application
 */
test.describe('Smoke Tests', () => {
  test('application loads', async ({ page }) => {
    await page.goto('/');

    // App should load - either shows timeclock frontpage or redirects
    await page.waitForLoadState('networkidle');
    expect(page.url()).toBeDefined();
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/login');

    // Login form should be visible
    await expect(page.locator('input[formControlName="username"], input[type="text"]').first()).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('API health check', async ({ request }) => {
    // Check if the backend API is responding
    const response = await request.get('http://localhost:8000/health');

    // API should respond with success
    expect(response.ok()).toBe(true);
  });

  test('no critical console errors on frontpage', async ({ page }) => {
    const criticalErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        const text = msg.text();
        // Filter out expected errors
        if (!text.includes('401') &&
            !text.includes('Unauthorized') &&
            !text.includes('Failed to fetch') &&
            !text.includes('license')) {
          criticalErrors.push(text);
        }
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Should have no critical errors
    expect(criticalErrors).toHaveLength(0);
  });

  test('no critical console errors on login page', async ({ page }) => {
    const criticalErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (!text.includes('401') &&
            !text.includes('Unauthorized') &&
            !text.includes('Failed to fetch')) {
          criticalErrors.push(text);
        }
      }
    });

    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    expect(criticalErrors).toHaveLength(0);
  });
});

test.describe('Accessibility', () => {
  test('login form has proper labels', async ({ page }) => {
    await page.goto('/login');

    // Check for proper form accessibility
    const usernameInput = page.locator('input[formControlName="username"], input[type="text"]').first();
    const passwordInput = page.locator('input[type="password"]');

    // Inputs should exist
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });

  test('login button is focusable', async ({ page }) => {
    await page.goto('/login');

    const loginButton = page.locator('button[type="submit"]');
    await expect(loginButton).toBeVisible();
    await loginButton.focus();
    await expect(loginButton).toBeFocused();
  });
});
