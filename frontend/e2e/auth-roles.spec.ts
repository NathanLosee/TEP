import { test, expect } from './fixtures/auth.fixture';
import { AuthRolesPage, AuthRoleFormDialog, AuthRoleDetailsDialog } from './pages/auth-roles.page';

test.describe('Auth Role Management', () => {
  test.describe('Role List', () => {
    test('should display auth roles page', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      await rolesPage.goto();

      await expect(page).toHaveURL(/\/admin\/auth-roles/);
    });

    test('should show roles table or empty state', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      await rolesPage.goto();

      const tableVisible = await rolesPage.roleTable.isVisible().catch(() => false);
      const emptyVisible = await rolesPage.emptyState.isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should display root role', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      await rolesPage.goto();

      // Root role should always exist
      const roleCount = await rolesPage.getRoleCount();
      expect(roleCount).toBeGreaterThan(0);
    });

    test('should show permission chips preview', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      await rolesPage.goto();

      // Roles should have permission chips displayed
      const chips = page.locator('mat-chip, .permission-chip');
      const chipCount = await chips.count();

      // At least the root role should have permissions displayed
      expect(chipCount).toBeGreaterThan(0);
    });
  });

  test.describe('Add Role', () => {
    test('should have add role button', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      await rolesPage.goto();

      await expect(rolesPage.addRoleButton).toBeVisible();
    });

    test('should open add role dialog', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      const formDialog = new AuthRoleFormDialog(page);

      await rolesPage.goto();
      await rolesPage.clickAddRole();

      await formDialog.expectOpen();
    });

    test('should show permission checkboxes in form', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      const formDialog = new AuthRoleFormDialog(page);

      await rolesPage.goto();
      await rolesPage.clickAddRole();
      await formDialog.expectOpen();

      // Should have permission checkboxes
      const checkboxCount = await formDialog.permissionCheckboxes.count();
      expect(checkboxCount).toBeGreaterThan(0);

      await formDialog.cancel();
    });

    test('should validate required name field', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      const formDialog = new AuthRoleFormDialog(page);

      await rolesPage.goto();
      await rolesPage.clickAddRole();
      await formDialog.expectOpen();

      // Try to save without name
      await formDialog.save();

      // Dialog should still be open (validation failed)
      await formDialog.expectOpen();

      await formDialog.cancel();
    });
  });

  test.describe('Role Details', () => {
    test('should show role details on view action', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      const detailsDialog = new AuthRoleDetailsDialog(page);

      await rolesPage.goto();

      const roleCount = await rolesPage.getRoleCount();
      if (roleCount > 0) {
        // Click view on first role
        const viewButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("visibility"))').first();
        const buttonVisible = await viewButton.isVisible().catch(() => false);

        if (buttonVisible) {
          await viewButton.click();
          await detailsDialog.expectOpen();
          await detailsDialog.close();
        }
      }
    });
  });

  test.describe('Role Actions', () => {
    test('should have edit and delete actions', async ({ authenticatedPage, page }) => {
      const rolesPage = new AuthRolesPage(page);
      await rolesPage.goto();

      const roleCount = await rolesPage.getRoleCount();
      if (roleCount > 0) {
        // Should have action buttons
        const editButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("edit"))').first();
        const deleteButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("delete"))').first();

        const editVisible = await editButton.isVisible().catch(() => false);
        const deleteVisible = await deleteButton.isVisible().catch(() => false);

        expect(editVisible || deleteVisible).toBe(true);
      }
    });
  });
});
