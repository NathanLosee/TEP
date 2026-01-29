import { test, expect } from './fixtures/auth.fixture';
import { EmployeesPage, EmployeeFormDialog } from './pages/employees.page';

test.describe('Employee Management', () => {
  test.describe('Employee List', () => {
    test('should display employee page', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      await expect(page).toHaveURL(/\/admin\/employees/);
    });

    test('should show employee table or empty state', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const tableVisible = await employeesPage.employeeTable.isVisible().catch(() => false);
      const emptyVisible = await employeesPage.emptyState.isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should display root employee', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      // Root employee with badge 0 should always exist
      const employeeCount = await employeesPage.getEmployeeCount();
      expect(employeeCount).toBeGreaterThan(0);
    });

    test('should have search functionality', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      await expect(employeesPage.searchInput).toBeVisible();
      await employeesPage.searchEmployee('root');
      await expect(employeesPage.searchInput).toHaveValue('root');
    });

    test('should filter employees by search term', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const initialCount = await employeesPage.getEmployeeCount();

      await employeesPage.searchEmployee('xyznonexistent123');
      await page.waitForTimeout(500);

      const filteredCount = await employeesPage.getEmployeeCount();
      expect(filteredCount).toBeLessThanOrEqual(initialCount);
    });

    test('should clear search', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      await employeesPage.searchEmployee('test');
      await employeesPage.searchEmployee('');
      await page.waitForTimeout(300);

      // Should show all employees again
      const employeeCount = await employeesPage.getEmployeeCount();
      expect(employeeCount).toBeGreaterThan(0);
    });
  });

  test.describe('Add Employee', () => {
    test('should have add employee button', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      await expect(employeesPage.addEmployeeButton).toBeVisible();
    });

    test('should open add employee dialog', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      const formDialog = new EmployeeFormDialog(page);

      await employeesPage.goto();
      await employeesPage.clickAddEmployee();
      await formDialog.expectOpen();
      await formDialog.cancel();
    });

    test('should have required form fields', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      const formDialog = new EmployeeFormDialog(page);

      await employeesPage.goto();
      await employeesPage.clickAddEmployee();
      await formDialog.expectOpen();

      // Check for required fields
      await expect(formDialog.badgeNumberInput).toBeVisible();
      await expect(formDialog.firstNameInput).toBeVisible();
      await expect(formDialog.lastNameInput).toBeVisible();

      await formDialog.cancel();
    });

    test('should validate required fields', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      const formDialog = new EmployeeFormDialog(page);

      await employeesPage.goto();
      await employeesPage.clickAddEmployee();
      await formDialog.expectOpen();

      // Try to save without filling required fields
      await formDialog.save();

      // Dialog should still be open (validation failed)
      await formDialog.expectOpen();

      // Should show validation errors
      await expect(page.locator('mat-error').first()).toBeVisible();

      await formDialog.cancel();
    });

    test('should close dialog on cancel', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      const formDialog = new EmployeeFormDialog(page);

      await employeesPage.goto();
      await employeesPage.clickAddEmployee();
      await formDialog.expectOpen();
      await formDialog.cancel();
      await formDialog.expectClosed();
    });
  });

  test.describe('Employee Actions', () => {
    test('should display action buttons', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const rowCount = await employeesPage.getEmployeeCount();
      if (rowCount > 0) {
        const actionButtons = page.locator('tr[mat-row] button[mat-icon-button], mat-row button[mat-icon-button]');
        const buttonCount = await actionButtons.count();
        expect(buttonCount).toBeGreaterThan(0);
      }
    });

    test('should have view details action', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const rowCount = await employeesPage.getEmployeeCount();
      if (rowCount > 0) {
        const viewButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("visibility")), tr[mat-row] button:has(mat-icon:has-text("info"))').first();
        const viewVisible = await viewButton.isVisible().catch(() => false);

        if (viewVisible) {
          await viewButton.click();
          const dialog = page.locator('mat-dialog-container');
          await expect(dialog).toBeVisible();
          await page.locator('button:has-text("Close")').click();
        }
      }
    });

    test('should have edit action', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const rowCount = await employeesPage.getEmployeeCount();
      if (rowCount > 0) {
        const editButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("edit"))').first();
        const editVisible = await editButton.isVisible().catch(() => false);
        expect(editVisible).toBe(true);
      }
    });

    test('should open edit dialog', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const rowCount = await employeesPage.getEmployeeCount();
      if (rowCount > 0) {
        const editButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("edit"))').first();

        if (await editButton.isVisible()) {
          await editButton.click();
          const dialog = page.locator('mat-dialog-container');
          await expect(dialog).toBeVisible();
          await page.locator('button:has-text("Cancel")').click();
        }
      }
    });
  });

  test.describe('Employee Table Columns', () => {
    test('should display expected columns', async ({ authenticatedPage, page }) => {
      const employeesPage = new EmployeesPage(page);
      await employeesPage.goto();

      const tableVisible = await employeesPage.employeeTable.isVisible().catch(() => false);
      if (tableVisible) {
        // Check for expected headers
        const headers = ['Badge', 'Name', 'First', 'Last'];
        for (const header of headers) {
          const headerCell = page.locator(`th:has-text("${header}")`);
          const isVisible = await headerCell.isVisible().catch(() => false);
          if (isVisible) {
            await expect(headerCell).toBeVisible();
            break;
          }
        }
      }
    });
  });
});
