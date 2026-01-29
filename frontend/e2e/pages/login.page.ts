import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object for the Login page
 */
export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  readonly snackbarError: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.locator('input[formControlName="username"]');
    this.passwordInput = page.locator('input[formControlName="password"]');
    this.loginButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message, mat-error');
    this.snackbarError = page.locator('mat-snack-bar, .snack-error');
  }

  async goto() {
    await this.page.goto('/login');
    await this.page.waitForLoadState('networkidle');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async expectLoginPage() {
    await expect(this.usernameInput).toBeVisible();
    await expect(this.passwordInput).toBeVisible();
    await expect(this.loginButton).toBeVisible();
  }

  async expectError(errorText?: string) {
    // Check for either inline error or snackbar
    const inlineErrorVisible = await this.errorMessage.isVisible().catch(() => false);
    const snackbarVisible = await this.snackbarError.isVisible().catch(() => false);

    expect(inlineErrorVisible || snackbarVisible).toBe(true);

    if (errorText) {
      if (inlineErrorVisible) {
        await expect(this.errorMessage).toContainText(errorText);
      } else if (snackbarVisible) {
        await expect(this.snackbarError).toContainText(errorText);
      }
    }
  }

  async expectNoError() {
    const inlineErrorVisible = await this.errorMessage.isVisible().catch(() => false);
    const snackbarVisible = await this.snackbarError.isVisible().catch(() => false);
    expect(inlineErrorVisible || snackbarVisible).toBe(false);
  }

  async expectRedirectedAfterLogin() {
    await expect(this.page).not.toHaveURL(/\/login/, { timeout: 10000 });
  }
}
