import { defineConfig, devices } from '@playwright/test';

/**
 * TAP E2E Test Configuration
 *
 * To run E2E tests:
 * 1. Start the backend: cd .. && python -m uvicorn src.main:app --reload
 * 2. Start the frontend: npm start
 * 3. Run tests: npx playwright test
 *
 * Or use the webServer config below to auto-start servers.
 */
export default defineConfig({
  testDir: './e2e',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env['CI'],
  /* Retry on CI only */
  retries: process.env['CI'] ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env['CI'] ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [['html'], ['list']],
  /* Test timeout - increased for slower operations */
  timeout: 30000,
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env['PLAYWRIGHT_TEST_BASE_URL'] ?? 'http://localhost:4200',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Screenshot on failure */
    screenshot: 'only-on-failure',

    /* Video on failure */
    video: 'on-first-retry',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Uncomment to test on Firefox
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // Uncomment to test on WebKit (Safari)
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  /* Web server configuration - uncomment to auto-start servers for tests */
  // webServer: [
  //   {
  //     command: 'cd .. && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000',
  //     url: 'http://localhost:8000/health',
  //     reuseExistingServer: !process.env['CI'],
  //     timeout: 120000,
  //   },
  //   {
  //     command: 'npm start',
  //     url: 'http://localhost:4200',
  //     reuseExistingServer: !process.env['CI'],
  //     timeout: 120000,
  //   },
  // ],
});
