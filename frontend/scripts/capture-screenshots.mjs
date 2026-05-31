/**
 * Captures demo screenshots of the running app for the README.
 * Requires the stack to be up (docker compose up). Run: `make screenshots`.
 */
import { chromium } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL ?? "http://localhost:3000";
const OUT = "../docs/screenshots";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

// Listing page
await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
await page.waitForSelector('a[href^="/salons/"]');
await page.screenshot({ path: `${OUT}/listing.png`, fullPage: false });

// Detail page
await page.locator('a[href^="/salons/"]').first().click();
await page.waitForURL(/\/salons\/\d+/);
await page.waitForSelector("text=AI review summary");
await page.screenshot({ path: `${OUT}/detail.png`, fullPage: false });

// Search results
await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
await page.getByRole("searchbox").fill("hair coloring in Mokotów");
await page.getByRole("button", { name: "Search" }).click();
await page.waitForSelector("text=/Semantic|Keyword/");
await page.screenshot({ path: `${OUT}/search.png`, fullPage: false });

await browser.close();
console.log("Saved listing.png, detail.png, search.png to docs/screenshots/");
