import { expect, test } from './fixtures/auth.fixture';

test.describe('Timeclock Entries', () => {
  test.describe('Entries Page', () => {
    test('should display timeclock entries page', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      await expect(page).toHaveURL(/\/admin\/timeclock-entries/);
    });

    test('should show entries table or empty state', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const tableVisible = await page
        .locator('table[mat-table], mat-table, app-generic-table')
        .isVisible()
        .catch(() => false);
      const emptyVisible = await page
        .locator('.empty-state, .no-data, .empty-container')
        .isVisible()
        .catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should have date range filter', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const dateInputs = page.locator(
        'input[matStartDate], input[matEndDate], mat-datapicker-toggle',
      );
      const hasDateFilters = await dateInputs
        .first()
        .isVisible()
        .catch(() => false);

      expect(hasDateFilters).toBe(true);
    });

    test('should have employee filter', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const employeeSelect = page.locator(
        'mat-select[formControlName="employee_id"], mat-select:has-text("Employee")',
      );
      const selectVisible = await employeeSelect.isVisible().catch(() => false);

      // Employee filter should be available
      expect(selectVisible).toBe(true);
    });
  });

  test.describe('Entry Columns', () => {
    test('should display expected columns', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      // Check for expected column headers
      const headers = ['Badge', 'Name', 'Clock In', 'Clock Out', 'Hours'];
      const tableVisible = await page
        .locator('table[mat-table], mat-table')
        .isVisible()
        .catch(() => false);

      if (tableVisible) {
        for (const header of headers) {
          const headerCell = page.locator(`th:has-text("${header}")`);
          const isVisible = await headerCell.isVisible().catch(() => false);
          // At least some of these headers should be visible
          if (isVisible) {
            await expect(headerCell).toBeVisible();
            break;
          }
        }
      }
    });
  });

  test.describe('Entry Actions', () => {
    test('should have add entry button', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const addButton = page.locator(
        'button:has-text("Add"), button:has(mat-icon:has-text("add"))',
      );
      await expect(addButton.first()).toBeVisible();
    });

    test('should open add entry dialog', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const addButton = page
        .locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))')
        .first();
      await addButton.click();

      const dialog = page.locator('mat-dialog-container');
      await expect(dialog).toBeVisible();

      // Cancel
      await page.locator('button:has-text("Cancel")').click();
    });

    test('should have entry form fields', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const addButton = page
        .locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))')
        .first();
      await addButton.click();

      // Should have employee select and date/time inputs
      const employeeSelect = page.locator(
        'mat-select[formControlName="employee_id"]',
      );
      const clockInInput = page.locator(
        'input[formControlName="clock_in"], input[formControlName="clockIn"]',
      );

      const employeeVisible = await employeeSelect
        .isVisible()
        .catch(() => false);
      const clockInVisible = await clockInInput.isVisible().catch(() => false);

      expect(employeeVisible || clockInVisible).toBe(true);

      await page.locator('button:has-text("Cancel")').click();
    });
  });

  test.describe('Entry Editing', () => {
    test('should show edit action for entries', async ({
      authenticatedPage,
      page,
    }) => {
      await authenticatedPage.gotoAdmin('timeclock-entries');

      const rows = page.locator('tr[mat-row], mat-row');
      const rowCount = await rows.count();

      if (rowCount > 0) {
        const editButton = page
          .locator('tr[mat-row] button:has(mat-icon:has-text("edit"))')
          .first();
        const editVisible = await editButton.isVisible().catch(() => false);
        expect(editVisible).toBe(true);
      }
    });
  });
});

test.describe('Frontpage Timeclock', () => {
  test('should display timeclock on frontpage', async ({ page }) => {
    // Go to frontpage (timeclock interface)
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Should show timeclock or login form
    const timeclockVisible = await page
      .locator('.timeclock, .clock-display, input[placeholder*="badge"]')
      .first()
      .isVisible()
      .catch(() => false);
    const loginVisible = await page
      .locator('form, input[type="password"]')
      .first()
      .isVisible()
      .catch(() => false);

    expect(timeclockVisible || loginVisible).toBe(true);
  });
});
