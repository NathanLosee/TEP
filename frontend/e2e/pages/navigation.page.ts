import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object for navigation and common elements
 * All admin routes are under /admin/
 */
export class NavigationPage {
  readonly page: Page;
  readonly sideNav: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.sideNav = page.locator('mat-sidenav, .sidenav, mat-nav-list');
    this.userMenu = page.locator('[data-testid="user-menu"], .user-menu, button:has-text("account_circle")');
    this.logoutButton = page.locator('button:has-text("Logout"), [data-testid="logout-button"]');
  }

  /**
   * Navigate to an admin route by clicking on the nav link
   */
  async navigateTo(routeName: string) {
    // Map of route names to their nav link text patterns
    const linkTextMap: Record<string, string> = {
      dashboard: 'Dashboard',
      employees: 'Employee',
      'timeclock-entries': 'Timeclock',
      departments: 'Department',
      'org-units': 'Org',
      'holiday-groups': 'Holiday',
      users: 'User',
      'auth-roles': 'Auth Role',
      'registered-browsers': 'Browser',
      reports: 'Report',
      'event-logs': 'Event',
      license: 'License',
      settings: 'Settings',
    };

    const linkText = linkTextMap[routeName];
    if (linkText) {
      // Find and click the nav link containing the text
      const link = this.page.locator(`mat-nav-list a:has-text("${linkText}"), .nav-list a:has-text("${linkText}")`).first();
      await link.click();
      // Wait for navigation to complete
      await this.page.waitForLoadState('networkidle');
    } else {
      // Direct navigation as fallback
      await this.page.goto(`/admin/${routeName}`);
      await this.page.waitForLoadState('networkidle');
    }
  }

  /**
   * Navigate directly to an admin route via URL
   */
  async gotoAdmin(route: string = 'dashboard') {
    await this.page.goto(`/admin/${route}`);
    await this.page.waitForLoadState('networkidle');
  }

  async logout() {
    // Try to find and click user menu first
    const userMenuVisible = await this.userMenu.isVisible().catch(() => false);
    if (userMenuVisible) {
      await this.userMenu.click();
    }
    await this.logoutButton.click();
  }

  async expectLoggedIn() {
    // User should see some navigation elements when logged in
    await expect(this.page.locator('mat-sidenav-container, .main-container, mat-nav-list').first()).toBeVisible();
  }

  async expectLoggedOut() {
    // User should be on login page when logged out
    await expect(this.page).toHaveURL(/\/login/);
  }

  /**
   * Get the page title text
   */
  async getPageTitle(): Promise<string> {
    const titleElement = this.page.locator('h1, h2, .page-title, mat-toolbar .title').first();
    return await titleElement.textContent() || '';
  }
}
