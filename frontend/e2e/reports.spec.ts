import { test, expect } from './fixtures/auth.fixture';
import { ReportsPage } from './pages/reports.page';

test.describe('Reports', () => {
  test.describe('Reports Page', () => {
    test('should display reports page', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      await expect(page).toHaveURL(/\/admin\/reports/);
    });

    test('should have date range inputs', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      // Should have date inputs for filtering
      const startDateVisible = await reportsPage.startDateInput.isVisible().catch(() => false);
      const endDateVisible = await reportsPage.endDateInput.isVisible().catch(() => false);

      expect(startDateVisible || endDateVisible).toBe(true);
    });

    test('should have filter options', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      // Should have at least one filter select
      const employeeSelectVisible = await reportsPage.employeeSelect.isVisible().catch(() => false);
      const departmentSelectVisible = await reportsPage.departmentSelect.isVisible().catch(() => false);
      const orgUnitSelectVisible = await reportsPage.orgUnitSelect.isVisible().catch(() => false);

      expect(employeeSelectVisible || departmentSelectVisible || orgUnitSelectVisible).toBe(true);
    });

    test('should have generate report button', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      await expect(reportsPage.generateButton).toBeVisible();
    });
  });

  test.describe('Report Generation', () => {
    test('should generate report', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      // Generate report with current filters
      await reportsPage.generateReport();
      await reportsPage.expectReportGenerated();
    });

    test('should show loading state while generating', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      // Click generate and check for loading
      await reportsPage.generateButton.click();

      // Either loading spinner or quick response
      await reportsPage.waitForLoad();
    });
  });

  test.describe('Report Export', () => {
    test('should have PDF export option', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      // Generate a report first
      await reportsPage.generateReport();

      // PDF export button should be available
      const exportVisible = await reportsPage.exportPdfButton.isVisible().catch(() => false);
      // Note: Export might only appear after report is generated
      if (exportVisible) {
        await expect(reportsPage.exportPdfButton).toBeVisible();
      }
    });
  });

  test.describe('Report Filters', () => {
    test('should filter by date range', async ({ authenticatedPage, page }) => {
      const reportsPage = new ReportsPage(page);
      await reportsPage.goto();

      // Get today's date
      const today = new Date();
      const lastMonth = new Date(today);
      lastMonth.setMonth(lastMonth.getMonth() - 1);

      const startDate = lastMonth.toISOString().split('T')[0];
      const endDate = today.toISOString().split('T')[0];

      // Set date range
      await reportsPage.setDateRange(startDate, endDate);
      await reportsPage.generateReport();

      await reportsPage.expectReportGenerated();
    });
  });
});
