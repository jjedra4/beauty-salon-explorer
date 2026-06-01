import { expect, test } from "@playwright/test";

/**
 * End-to-end happy paths across the redesigned flow:
 *   - directory: browse → filter → open detail
 *   - detail: edit → persist
 *   - discover: AI prompt on the home hero → /search results
 * Requires the backend at :8000 with seed data loaded (see `make e2e`).
 */

const salonLink = 'a[href^="/salons/"]';

test("browse the directory, filter, and open a salon detail", async ({ page }) => {
  await page.goto("/browse");
  await expect(page.getByRole("heading", { name: "Browse every salon" })).toBeVisible();

  // Salon cards load from the API.
  await expect(page.locator(salonLink).first()).toBeVisible();

  // Filtering by district updates the URL and the results.
  await page.getByLabel("Filter by district").selectOption("Mokotów");
  await expect(page).toHaveURL(/district=Mokot/);
  await expect(page.locator(salonLink).first()).toBeVisible();

  // Open the first salon's detail page.
  await page.locator(salonLink).first().click();
  await expect(page).toHaveURL(/\/salons\/\d+/);
  await expect(page.getByRole("button", { name: "Edit" })).toBeVisible();
});

test("edit a salon and persist the change", async ({ page }) => {
  await page.goto("/browse");
  await page.locator(salonLink).first().click();
  await expect(page).toHaveURL(/\/salons\/\d+/);

  await page.getByRole("button", { name: "Edit" }).click();

  const newName = `E2E Salon ${Date.now()}`;
  const nameInput = page.getByLabel("Salon name");
  await expect(nameInput).toBeVisible();
  await nameInput.fill(newName);
  await page.getByRole("button", { name: "Save changes" }).click();

  // The updated name is shown, and persists across a reload.
  await expect(page.getByRole("heading", { name: newName })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: newName })).toBeVisible();
});

test("the home hero prompt routes to search results with a mode badge", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("searchbox").fill("hair coloring");
  await page.getByRole("button", { name: "Ask" }).click();

  await expect(page).toHaveURL(/\/search\?q=hair/);
  // Either semantic (with an API key) or keyword fallback is acceptable.
  await expect(page.getByText(/Semantic|Keyword/)).toBeVisible();
  await expect(page.locator(salonLink).first()).toBeVisible();
});
