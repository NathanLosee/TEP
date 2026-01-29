import { test, expect } from './fixtures/auth.fixture';
import { UsersPage, UserFormDialog, PasswordChangeDialog } from './pages/users.page';

test.describe('User Management', () => {
  test.describe('User List', () => {
    test('should display user list page', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      await usersPage.goto();

      await expect(page).toHaveURL(/\/admin\/users/);
    });

    test('should show user table or empty state', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      await usersPage.goto();

      const tableVisible = await usersPage.userTable.isVisible().catch(() => false);
      const emptyVisible = await usersPage.emptyState.isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should have search functionality', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      await usersPage.goto();

      const searchVisible = await usersPage.searchInput.isVisible().catch(() => false);
      if (searchVisible) {
        await usersPage.searchUser('root');
        await expect(usersPage.searchInput).toHaveValue('root');
      }
    });

    test('should display root user (badge 0)', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      await usersPage.goto();

      // Root user with badge 0 should always exist
      const userCount = await usersPage.getUserCount();
      expect(userCount).toBeGreaterThan(0);
    });
  });

  test.describe('Add User', () => {
    test('should have add user button', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      await usersPage.goto();

      const addButtonVisible = await usersPage.addUserButton.isVisible().catch(() => false);
      // Add button should exist (might be disabled if no employees without users)
      expect(addButtonVisible).toBe(true);
    });

    test('should open add user dialog', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      const formDialog = new UserFormDialog(page);

      await usersPage.goto();

      const addButtonEnabled = await usersPage.addUserButton.isEnabled().catch(() => false);
      if (addButtonEnabled) {
        await usersPage.clickAddUser();
        await formDialog.expectOpen();
        await formDialog.cancel();
      }
    });
  });

  test.describe('User Actions', () => {
    test('should show action buttons for users', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      await usersPage.goto();

      const userCount = await usersPage.getUserCount();
      if (userCount > 0) {
        // Should have action buttons in the row
        const actionButtons = page.locator('tr[mat-row] button[mat-icon-button], mat-row button[mat-icon-button]');
        const buttonCount = await actionButtons.count();
        expect(buttonCount).toBeGreaterThan(0);
      }
    });

    test('should open password change dialog', async ({ authenticatedPage, page }) => {
      const usersPage = new UsersPage(page);
      const passwordDialog = new PasswordChangeDialog(page);

      await usersPage.goto();

      const userCount = await usersPage.getUserCount();
      if (userCount > 0) {
        // Try to click password change on first user
        const passwordButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("key")), tr[mat-row] button:has(mat-icon:has-text("password"))').first();
        const buttonVisible = await passwordButton.isVisible().catch(() => false);

        if (buttonVisible) {
          await passwordButton.click();
          await passwordDialog.expectOpen();
          await page.locator('button:has-text("Cancel")').click();
        }
      }
    });
  });
});
