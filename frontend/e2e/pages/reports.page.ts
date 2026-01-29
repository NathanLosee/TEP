import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object for Reports
 */
export class ReportsPage {
  readonly page: Page;
  readonly startDateInput: Locator;
  readonly endDateInput: Locator;
  readonly employeeSelect: Locator;
  readonly departmentSelect: Locator;
  readonly orgUnitSelect: Locator;
  readonly generateButton: Locator;
  readonly exportPdfButton: Locator;
  readonly reportTable: Locator;
  readonly loadingSpinner: Locator;
  readonly noDataMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.startDateInput = page.locator('input[formControlName="startDate"], input[matStartDate]');
    this.endDateInput = page.locator('input[formControlName="endDate"], input[matEndDate]');
    this.employeeSelect = page.locator('mat-select[formControlName="employee_id"]');
    this.departmentSelect = page.locator('mat-select[formControlName="department_id"]');
    this.orgUnitSelect = page.locator('mat-select[formControlName="org_unit_id"]');
    this.generateButton = page.locator('button:has-text("Generate"), button:has-text("Run")');
    this.exportPdfButton = page.locator('button:has-text("PDF"), button:has-text("Export")');
    this.reportTable = page.locator('table[mat-table], mat-table');
    this.loadingSpinner = page.locator('mat-spinner, mat-progress-spinner');
    this.noDataMessage = page.locator('.no-data, .empty-state, text=No data');
  }

  async goto() {
    await this.page.goto('/admin/reports');
    await this.waitForLoad();
  }

  async waitForLoad() {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
    await this.page.waitForLoadState('networkidle');
  }

  async setDateRange(startDate: string, endDate: string) {
    await this.startDateInput.fill(startDate);
    await this.endDateInput.fill(endDate);
  }

  async selectEmployee(employeeName: string) {
    await this.employeeSelect.click();
    await this.page.locator(`mat-option:has-text("${employeeName}")`).click();
  }

  async selectDepartment(departmentName: string) {
    await this.departmentSelect.click();
    await this.page.locator(`mat-option:has-text("${departmentName}")`).click();
  }

  async generateReport() {
    await this.generateButton.click();
    await this.waitForLoad();
  }

  async exportPdf() {
    await this.exportPdfButton.click();
  }

  async expectReportGenerated() {
    // Either table with data or no data message
    const tableVisible = await this.reportTable.isVisible().catch(() => false);
    const noDataVisible = await this.noDataMessage.isVisible().catch(() => false);
    expect(tableVisible || noDataVisible).toBe(true);
  }
}

/**
 * Page Object for Event Log Management
 */
export class EventLogsPage {
  readonly page: Page;
  readonly dateRangeStart: Locator;
  readonly dateRangeEnd: Locator;
  readonly eventTypeFilter: Locator;
  readonly searchInput: Locator;
  readonly logTable: Locator;
  readonly logRows: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dateRangeStart = page.locator('input[matStartDate], input[formControlName="startDate"]');
    this.dateRangeEnd = page.locator('input[matEndDate], input[formControlName="endDate"]');
    this.eventTypeFilter = page.locator('mat-select[formControlName="eventType"]');
    this.searchInput = page.locator('input[placeholder*="Search"], input[formControlName="search"]');
    this.logTable = page.locator('table[mat-table], mat-table, app-generic-table table');
    this.logRows = page.locator('tr[mat-row], mat-row');
    this.loadingSpinner = page.locator('mat-spinner, mat-progress-spinner');
    this.emptyState = page.locator('.empty-state, .no-data, .empty-container');
  }

  async goto() {
    await this.page.goto('/admin/event-logs');
    await this.waitForLoad();
  }

  async waitForLoad() {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
    await this.page.waitForLoadState('networkidle');
  }

  async getLogCount(): Promise<number> {
    return await this.logRows.count();
  }

  async clickLogDetails(index: number = 0) {
    const viewButton = this.logRows.nth(index).locator('button:has(mat-icon:has-text("visibility"))');
    await viewButton.click();
  }

  async expectLogsDisplayed() {
    const tableVisible = await this.logTable.isVisible().catch(() => false);
    const emptyVisible = await this.emptyState.isVisible().catch(() => false);
    expect(tableVisible || emptyVisible).toBe(true);
  }
}

/**
 * Page Object for Event Log Detail Dialog
 */
export class EventLogDetailDialog {
  readonly page: Page;
  readonly dialog: Locator;
  readonly eventType: Locator;
  readonly timestamp: Locator;
  readonly details: Locator;
  readonly closeButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.locator('mat-dialog-container');
    this.eventType = page.locator('.event-type, h2[mat-dialog-title]');
    this.timestamp = page.locator('.timestamp, .event-time');
    this.details = page.locator('.event-details, .log-details, pre');
    this.closeButton = page.locator('button:has-text("Close")');
  }

  async expectOpen() {
    await expect(this.dialog).toBeVisible();
  }

  async close() {
    await this.closeButton.click();
  }
}
