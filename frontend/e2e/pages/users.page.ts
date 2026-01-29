import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object for User Management
 */
export class UsersPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly addUserButton: Locator;
  readonly userTable: Locator;
  readonly userRows: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.locator('input[placeholder*="Search"], input[formControlName="search"]');
    this.addUserButton = page.locator('button:has-text("Add"), button:has-text("New User"), button:has(mat-icon:has-text("add"))');
    this.userTable = page.locator('table[mat-table], mat-table, app-generic-table table');
    this.userRows = page.locator('tr[mat-row], mat-row');
    this.loadingSpinner = page.locator('mat-spinner, mat-progress-spinner');
    this.emptyState = page.locator('.empty-state, .no-data, .empty-container');
  }

  async goto() {
    await this.page.goto('/admin/users');
    await this.waitForLoad();
  }

  async waitForLoad() {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
    await this.page.waitForLoadState('networkidle');
  }

  async searchUser(searchTerm: string) {
    await this.searchInput.fill(searchTerm);
    await this.page.waitForTimeout(300);
  }

  async clickAddUser() {
    await this.addUserButton.click();
  }

  async getUserCount(): Promise<number> {
    return await this.userRows.count();
  }

  async expectUserInTable(badgeNumber: string) {
    await expect(this.page.locator(`td:has-text("${badgeNumber}")`)).toBeVisible();
  }

  async clickUserAction(badgeNumber: string, action: 'edit' | 'delete' | 'password') {
    const row = this.page.locator(`tr:has-text("${badgeNumber}")`);
    let iconName = action === 'edit' ? 'edit' : action === 'delete' ? 'delete' : 'key';
    const actionButton = row.locator(`button:has(mat-icon:has-text("${iconName}"))`).first();
    await actionButton.click();
  }
}

/**
 * Page Object for User Form Dialog
 */
export class UserFormDialog {
  readonly page: Page;
  readonly dialog: Locator;
  readonly badgeNumberSelect: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.locator('mat-dialog-container');
    this.badgeNumberSelect = page.locator('mat-select[formControlName="badge_number"]');
    this.passwordInput = page.locator('input[formControlName="password"]');
    this.confirmPasswordInput = page.locator('input[formControlName="confirmPassword"]');
    this.saveButton = page.locator('button:has-text("Save"), button:has-text("Create")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
  }

  async expectOpen() {
    await expect(this.dialog).toBeVisible();
  }

  async expectClosed() {
    await expect(this.dialog).not.toBeVisible();
  }

  async fillForm(data: { password?: string }) {
    if (data.password) {
      await this.passwordInput.fill(data.password);
      if (await this.confirmPasswordInput.isVisible()) {
        await this.confirmPasswordInput.fill(data.password);
      }
    }
  }

  async save() {
    await this.saveButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }
}

/**
 * Page Object for Password Change Dialog
 */
export class PasswordChangeDialog {
  readonly page: Page;
  readonly dialog: Locator;
  readonly newPasswordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.locator('mat-dialog-container');
    this.newPasswordInput = page.locator('input[formControlName="newPassword"], input[formControlName="password"]');
    this.confirmPasswordInput = page.locator('input[formControlName="confirmPassword"]');
    this.saveButton = page.locator('button:has-text("Save"), button:has-text("Change")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
  }

  async expectOpen() {
    await expect(this.dialog).toBeVisible();
  }

  async fillAndSubmit(newPassword: string) {
    await this.newPasswordInput.fill(newPassword);
    if (await this.confirmPasswordInput.isVisible()) {
      await this.confirmPasswordInput.fill(newPassword);
    }
    await this.saveButton.click();
  }
}
