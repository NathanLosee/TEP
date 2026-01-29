import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object for Employee Management
 */
export class EmployeesPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly addEmployeeButton: Locator;
  readonly employeeTable: Locator;
  readonly employeeRows: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.locator('input[placeholder*="Search"], input[formControlName="search"]');
    this.addEmployeeButton = page.locator('button:has-text("Add"), button:has-text("New Employee")');
    this.employeeTable = page.locator('table[mat-table], mat-table');
    this.employeeRows = page.locator('tr[mat-row], mat-row');
    this.loadingSpinner = page.locator('mat-spinner, mat-progress-spinner');
    this.emptyState = page.locator('.empty-state, .no-data');
  }

  async goto() {
    await this.page.goto('/admin/employees');
    await this.waitForLoad();
  }

  async waitForLoad() {
    // Wait for loading to complete
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
    await this.page.waitForLoadState('networkidle');
  }

  async searchEmployee(searchTerm: string) {
    await this.searchInput.fill(searchTerm);
    await this.page.waitForTimeout(300); // Debounce
  }

  async clickAddEmployee() {
    await this.addEmployeeButton.click();
  }

  async getEmployeeCount(): Promise<number> {
    return await this.employeeRows.count();
  }

  async expectEmployeeInTable(badgeNumber: string) {
    await expect(this.page.locator(`td:has-text("${badgeNumber}")`)).toBeVisible();
  }

  async expectNoEmployees() {
    const rowCount = await this.getEmployeeCount();
    expect(rowCount).toBe(0);
  }

  async clickEmployeeAction(badgeNumber: string, action: 'edit' | 'delete' | 'view') {
    const row = this.page.locator(`tr:has-text("${badgeNumber}")`);
    const actionButton = row.locator(`button:has(mat-icon:has-text("${action === 'edit' ? 'edit' : action === 'delete' ? 'delete' : 'visibility'}"))`)
      .or(row.locator(`button[mattooltip*="${action}"]`));
    await actionButton.click();
  }
}

/**
 * Page Object for Employee Form Dialog
 */
export class EmployeeFormDialog {
  readonly page: Page;
  readonly dialog: Locator;
  readonly badgeNumberInput: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly payrollTypeSelect: Locator;
  readonly orgUnitSelect: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.locator('mat-dialog-container');
    this.badgeNumberInput = page.locator('input[formControlName="badge_number"]');
    this.firstNameInput = page.locator('input[formControlName="first_name"]');
    this.lastNameInput = page.locator('input[formControlName="last_name"]');
    this.payrollTypeSelect = page.locator('mat-select[formControlName="payroll_type"]');
    this.orgUnitSelect = page.locator('mat-select[formControlName="org_unit_id"]');
    this.saveButton = page.locator('button:has-text("Save"), button:has-text("Create")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
  }

  async expectOpen() {
    await expect(this.dialog).toBeVisible();
  }

  async expectClosed() {
    await expect(this.dialog).not.toBeVisible();
  }

  async fillEmployeeForm(data: {
    badgeNumber?: string;
    firstName?: string;
    lastName?: string;
    payrollType?: string;
  }) {
    if (data.badgeNumber) {
      await this.badgeNumberInput.fill(data.badgeNumber);
    }
    if (data.firstName) {
      await this.firstNameInput.fill(data.firstName);
    }
    if (data.lastName) {
      await this.lastNameInput.fill(data.lastName);
    }
    if (data.payrollType) {
      await this.payrollTypeSelect.click();
      await this.page.locator(`mat-option:has-text("${data.payrollType}")`).click();
    }
  }

  async save() {
    await this.saveButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }
}
