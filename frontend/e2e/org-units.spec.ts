import { test, expect } from './fixtures/auth.fixture';

test.describe('Organizational Units', () => {
  test.describe('Org Units Page', () => {
    test('should display org units page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      await expect(page).toHaveURL(/\/admin\/org-units/);
    });

    test('should show org units table or empty state', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      const tableVisible = await page.locator('table[mat-table], mat-table, app-generic-table').isVisible().catch(() => false);
      const emptyVisible = await page.locator('.empty-state, .no-data, .empty-container').isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should have add org unit button', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      const addButton = page.locator('button:has-text("Add"), button:has-text("New"), button:has(mat-icon:has-text("add"))');
      await expect(addButton.first()).toBeVisible();
    });

    test('should display root org unit', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      // Root org unit should always exist (created during setup)
      const rows = page.locator('tr[mat-row], mat-row');
      const rowCount = await rows.count();
      expect(rowCount).toBeGreaterThan(0);
    });
  });

  test.describe('Add Org Unit', () => {
    test('should open add org unit dialog', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))').first();
      await addButton.click();

      const dialog = page.locator('mat-dialog-container');
      await expect(dialog).toBeVisible();

      // Cancel
      await page.locator('button:has-text("Cancel")').click();
    });

    test('should have name input in form', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      const addButton = page.locator('button:has-text("Add"), button:has(mat-icon:has-text("add"))').first();
      await addButton.click();

      const nameInput = page.locator('input[formControlName="name"]');
      await expect(nameInput).toBeVisible();

      await page.locator('button:has-text("Cancel")').click();
    });
  });

  test.describe('Org Unit Actions', () => {
    test('should have view employees action', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      const rows = page.locator('tr[mat-row], mat-row');
      const rowCount = await rows.count();

      if (rowCount > 0) {
        const viewButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("people")), tr[mat-row] button:has(mat-icon:has-text("group"))').first();
        const viewVisible = await viewButton.isVisible().catch(() => false);
        expect(viewVisible).toBe(true);
      }
    });

    test('should open employees dialog', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('org-units');

      const rows = page.locator('tr[mat-row], mat-row');
      const rowCount = await rows.count();

      if (rowCount > 0) {
        const viewButton = page.locator('tr[mat-row] button:has(mat-icon:has-text("people")), tr[mat-row] button:has(mat-icon:has-text("group"))').first();

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

test.describe('Registered Browsers', () => {
  test.describe('Browsers Page', () => {
    test('should display registered browsers page', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('registered-browsers');

      await expect(page).toHaveURL(/\/admin\/registered-browsers/);
    });

    test('should show browsers table or empty state', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('registered-browsers');

      const tableVisible = await page.locator('table[mat-table], mat-table, app-generic-table').isVisible().catch(() => false);
      const emptyVisible = await page.locator('.empty-state, .no-data, .empty-container').isVisible().catch(() => false);

      expect(tableVisible || emptyVisible).toBe(true);
    });

    test('should have browser registration form', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('registered-browsers');

      // Should have form for registering browser
      const uuidInput = page.locator('input[formControlName="browser_uuid"]');
      const nameInput = page.locator('input[formControlName="browser_name"]');

      const uuidVisible = await uuidInput.isVisible().catch(() => false);
      const nameVisible = await nameInput.isVisible().catch(() => false);

      expect(uuidVisible || nameVisible).toBe(true);
    });
  });

  test.describe('Browser Registration', () => {
    test('should have generate UUID button', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('registered-browsers');

      const generateButton = page.locator('button:has-text("Generate"), button:has(mat-icon:has-text("refresh")), button:has(mat-icon:has-text("autorenew"))');
      const buttonVisible = await generateButton.first().isVisible().catch(() => false);

      expect(buttonVisible).toBe(true);
    });

    test('should generate UUID when button clicked', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('registered-browsers');

      const uuidInput = page.locator('input[formControlName="browser_uuid"]');
      const generateButton = page.locator('button:has-text("Generate"), button:has(mat-icon:has-text("refresh")), button:has(mat-icon:has-text("autorenew"))').first();

      if (await generateButton.isVisible()) {
        const initialValue = await uuidInput.inputValue();
        await generateButton.click();
        const newValue = await uuidInput.inputValue();

        // UUID should be generated (format: WORD-WORD-WORD-NN)
        expect(newValue).toMatch(/^[A-Z]+-[A-Z]+-[A-Z]+-\d{2}$/);
        expect(newValue).not.toBe(initialValue);
      }
    });
  });

  test.describe('Current Browser Status', () => {
    test('should display current browser status', async ({ authenticatedPage, page }) => {
      await authenticatedPage.gotoAdmin('registered-browsers');

      // Should show current browser info section
      const currentBrowserSection = page.locator('text=Current Browser, text=This Browser, .current-browser');
      const sectionVisible = await currentBrowserSection.first().isVisible().catch(() => false);

      // Current browser section should be visible
      expect(sectionVisible).toBe(true);
    });
  });
});
