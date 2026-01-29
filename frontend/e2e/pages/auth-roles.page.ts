import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object for Auth Role Management
 */
export class AuthRolesPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly addRoleButton: Locator;
  readonly roleTable: Locator;
  readonly roleRows: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.locator('input[placeholder*="Search"], input[formControlName="search"]');
    this.addRoleButton = page.locator('button:has-text("Add"), button:has-text("New"), button:has(mat-icon:has-text("add"))');
    this.roleTable = page.locator('table[mat-table], mat-table, app-generic-table table');
    this.roleRows = page.locator('tr[mat-row], mat-row');
    this.loadingSpinner = page.locator('mat-spinner, mat-progress-spinner');
    this.emptyState = page.locator('.empty-state, .no-data, .empty-container');
  }

  async goto() {
    await this.page.goto('/admin/auth-roles');
    await this.waitForLoad();
  }

  async waitForLoad() {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
    await this.page.waitForLoadState('networkidle');
  }

  async clickAddRole() {
    await this.addRoleButton.click();
  }

  async getRoleCount(): Promise<number> {
    return await this.roleRows.count();
  }

  async expectRoleInTable(roleName: string) {
    await expect(this.page.locator(`td:has-text("${roleName}")`)).toBeVisible();
  }

  async clickRoleAction(roleName: string, action: 'view' | 'edit' | 'delete') {
    const row = this.page.locator(`tr:has-text("${roleName}")`);
    const iconName = action === 'view' ? 'visibility' : action === 'edit' ? 'edit' : 'delete';
    const actionButton = row.locator(`button:has(mat-icon:has-text("${iconName}"))`).first();
    await actionButton.click();
  }
}

/**
 * Page Object for Auth Role Form Dialog
 */
export class AuthRoleFormDialog {
  readonly page: Page;
  readonly dialog: Locator;
  readonly nameInput: Locator;
  readonly permissionCheckboxes: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.locator('mat-dialog-container');
    this.nameInput = page.locator('input[formControlName="name"]');
    this.permissionCheckboxes = page.locator('mat-checkbox');
    this.saveButton = page.locator('button:has-text("Save"), button:has-text("Create")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
  }

  async expectOpen() {
    await expect(this.dialog).toBeVisible();
  }

  async expectClosed() {
    await expect(this.dialog).not.toBeVisible();
  }

  async fillForm(data: { name?: string }) {
    if (data.name) {
      await this.nameInput.fill(data.name);
    }
  }

  async togglePermission(permissionText: string) {
    const checkbox = this.page.locator(`mat-checkbox:has-text("${permissionText}")`);
    await checkbox.click();
  }

  async save() {
    await this.saveButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }
}

/**
 * Page Object for Auth Role Details Dialog
 */
export class AuthRoleDetailsDialog {
  readonly page: Page;
  readonly dialog: Locator;
  readonly roleName: Locator;
  readonly permissionsList: Locator;
  readonly usersList: Locator;
  readonly closeButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.locator('mat-dialog-container');
    this.roleName = page.locator('h2[mat-dialog-title], .dialog-title');
    this.permissionsList = page.locator('.permissions-list, mat-chip-set');
    this.usersList = page.locator('.users-list, .members-list');
    this.closeButton = page.locator('button:has-text("Close")');
  }

  async expectOpen() {
    await expect(this.dialog).toBeVisible();
  }

  async close() {
    await this.closeButton.click();
  }
}
