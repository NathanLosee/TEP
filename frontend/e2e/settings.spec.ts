import { test, expect } from './fixtures/auth.fixture';

test.describe('System Settings', () => {
  test.describe('Settings Page', () => {
    test('should display system settings page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('settings');

      await expect(page).toHaveURL(/\/admin\/settings/);
    });

    test('should have settings sections', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('settings');

      // Should have some form of settings UI
      const settingsForm = page.locator('form, mat-card, .settings-section');
      await expect(settingsForm.first()).toBeVisible();
    });

    test('should display theme/color settings', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('settings');

      // Look for theme-related settings
      const colorInputs = page.locator('input[type="color"], .color-picker');
      const colorInputVisible = await colorInputs.first().isVisible().catch(() => false);

      // Should have color customization
      expect(colorInputVisible).toBe(true);
    });

    test('should display logo upload option', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('settings');

      // Look for logo upload
      const fileInput = page.locator('input[type="file"]');
      const uploadButton = page.locator('button:has-text("Upload"), button:has-text("Logo")');

      const fileInputVisible = await fileInput.isVisible().catch(() => false);
      const uploadButtonVisible = await uploadButton.first().isVisible().catch(() => false);

      expect(fileInputVisible || uploadButtonVisible).toBe(true);
    });

    test('should have save button', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('settings');

      const saveButton = page.locator('button:has-text("Save"), button[type="submit"]');
      await expect(saveButton.first()).toBeVisible();
    });
  });

  test.describe('Theme Customization', () => {
    test('should allow changing primary color', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('settings');

      const colorInput = page.locator('input[type="color"]').first();
      const isVisible = await colorInput.isVisible().catch(() => false);

      if (isVisible) {
        // Color input should be interactive
        await expect(colorInput).toBeEnabled();
      }
    });
  });
});

test.describe('License Management', () => {
  test.describe('License Page', () => {
    test('should display license page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('license');

      await expect(page).toHaveURL(/\/admin\/license/);
    });

    test('should display license status', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('license');

      // Should show license status indicator
      const statusSection = page.locator('.license-status, mat-card, .status-badge, text=License');
      await expect(statusSection.first()).toBeVisible();
    });

    test('should show activation form or status', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('license');

      // If license is not activated, should show activation form
      const activationForm = page.locator('input[formControlName="license_key"]');
      const formVisible = await activationForm.isVisible().catch(() => false);

      // Or we're already activated
      const activatedIndicator = page.locator('.active, text=Active, .license-active');
      const isActivated = await activatedIndicator.first().isVisible().catch(() => false);

      expect(formVisible || isActivated).toBe(true);
    });

    test('should have activate button when not activated', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('license');

      const activationForm = page.locator('input[formControlName="license_key"]');
      const formVisible = await activationForm.isVisible().catch(() => false);

      if (formVisible) {
        const activateButton = page.locator('button:has-text("Activate")');
        await expect(activateButton).toBeVisible();
      }
    });
  });
});

test.describe('Departments Management', () => {
  test.describe('Departments Page', () => {
    test('should display departments page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('departments');

      await expect(page).toHaveURL(/\/admin\/departments/);
    });

    test('should show table or empty state', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('departments');

      const tableVisible = await page.locator('table[mat-table], mat-table, app-generic-table').isVisible().catch(() => false);
      const emptyVisible = await page.locator('.empty-state, .no-data, .empty-container').isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should have add department button', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('departments');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))');
      await expect(addButton.first()).toBeVisible();
    });
  });

  test.describe('Add Department', () => {
    test('should open add department dialog', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('departments');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))').first();
      await addButton.click();

      const dialog = page.locator('mat-dialog-container');
      await expect(dialog).toBeVisible();

      await page.locator('button:has-text("Cancel")').click();
    });

    test('should have name input', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('departments');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))').first();
      await addButton.click();

      const nameInput = page.locator('input[formControlName="name"]');
      await expect(nameInput).toBeVisible();

      await page.locator('button:has-text("Cancel")').click();
    });
  });

  test.describe('Department Actions', () => {
    test('should have view employees action', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('departments');

      const rows = page.locator('tr[mat-row], mat-row');
      const rowCount = await rows.count();

      if (rowCount > 0) {
        const viewButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("people")), tr[mat-row] button:has(mat-icon:has-text("group"))').first();
        const viewVisible = await viewButton.isVisible().catch(() => false);
        expect(viewVisible).toBe(true);
      }
    });
  });
});

test.describe('Holiday Groups', () => {
  test.describe('Holiday Groups Page', () => {
    test('should display holiday groups page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('holiday-groups');

      await expect(page).toHaveURL(/\/admin\/holiday-groups/);
    });

    test('should show table or empty state', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('holiday-groups');

      const tableVisible = await page.locator('table[mat-table], mat-table, app-generic-table').isVisible().catch(() => false);
      const emptyVisible = await page.locator('.empty-state, .no-data, .empty-container').isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should have add holiday group button', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('holiday-groups');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))');
      await expect(addButton.first()).toBeVisible();
    });
  });

  test.describe('Add Holiday Group', () => {
    test('should open add holiday group dialog', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('holiday-groups');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))').first();
      await addButton.click();

      const dialog = page.locator('mat-dialog-container');
      await expect(dialog).toBeVisible();

      await page.locator('button:has-text("Cancel")').click();
    });
  });

  test.describe('Holiday Group Details', () => {
    test('should show details on view action', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('holiday-groups');

      const rows = page.locator('tr[mat-row], mat-row');
      const rowCount = await rows.count();

      if (rowCount > 0) {
        const viewButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("visibility")), tr[mat-row] button:has(mat-icon:has-text("info"))').first();

        if (await viewButton.isVisible()) {
          await viewButton.click();

          const dialog = page.locator('mat-dialog-container');
          await expect(dialog).toBeVisible();

          await page.locator('button:has-text("Close")').click();
        }
      }
    });
  });
});
