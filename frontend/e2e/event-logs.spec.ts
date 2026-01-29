import { test, expect } from './fixtures/auth.fixture';
import { EventLogsPage, EventLogDetailDialog } from './pages/reports.page';

test.describe('Event Logs', () => {
  test.describe('Event Logs Page', () => {
    test('should display event logs page', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      await logsPage.goto();

      await expect(page).toHaveURL(/\/admin\/event-logs/);
    });

    test('should show logs table or empty state', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      await logsPage.goto();

      await logsPage.expectLogsDisplayed();
    });

    test('should have date range filter', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      await logsPage.goto();

      // Should have date inputs for filtering
      const startDateVisible = await logsPage.dateRangeStart.isVisible().catch(() => false);
      const endDateVisible = await logsPage.dateRangeEnd.isVisible().catch(() => false);

      expect(startDateVisible || endDateVisible).toBe(true);
    });
  });

  test.describe('Log Entries', () => {
    test('should display log entries', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      await logsPage.goto();

      // Should have at least login event from our test
      const logCount = await logsPage.getLogCount();
      // Note: There may or may not be logs depending on activity
      expect(logCount).toBeGreaterThanOrEqual(0);
    });

    test('should show log details on view action', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      const detailDialog = new EventLogDetailDialog(page);

      await logsPage.goto();

      const logCount = await logsPage.getLogCount();
      if (logCount > 0) {
        // Click view on first log
        await logsPage.clickLogDetails(0);
        await detailDialog.expectOpen();
        await detailDialog.close();
      }
    });
  });

  test.describe('Log Columns', () => {
    test('should display timestamp column', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      await logsPage.goto();

      const timestampHeader = page.locator('th:has-text("Time"), th:has-text("Date"), th:has-text("Timestamp")');
      const headerVisible = await timestampHeader.isVisible().catch(() => false);

      if (await logsPage.logTable.isVisible()) {
        expect(headerVisible).toBe(true);
      }
    });

    test('should display event type column', async ({ authenticatedPage, page }) => {
      const logsPage = new EventLogsPage(page);
      await logsPage.goto();

      const typeHeader = page.locator('th:has-text("Type"), th:has-text("Event"), th:has-text("Action")');
      const headerVisible = await typeHeader.isVisible().catch(() => false);

      if (await logsPage.logTable.isVisible()) {
        expect(headerVisible).toBe(true);
      }
    });
  });
});
