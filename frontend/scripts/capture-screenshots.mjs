/**
 * Captures demo screenshots of the running app for the README.
 * Requires the stack to be up (docker compose up). Run: `make screenshots`.
 */
import { chromium } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL ?? "http://localhost:3000";
const OUT = "../docs/screenshots";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

// Discover / hero — let the entrance animation settle and the ghost prompt type.
await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
await page.getByRole("searchbox").waitFor();
await page.waitForTimeout(1600);
await page.screenshot({ path: `${OUT}/hero.png`, fullPage: false });

// Search results — run a query from the hero.
await page.getByRole("searchbox").fill("hair coloring in Mokotów");
await page.getByRole("button", { name: "Ask" }).click();
await page.waitForURL(/\/search\?q=/);
await page.waitForSelector("text=/Semantic|Keyword/");
await page.waitForTimeout(700);
await page.screenshot({ path: `${OUT}/search.png`, fullPage: false });

// Detail — open the first salon from the directory.
await page.goto(`${BASE}/browse`, { waitUntil: "networkidle" });
await page.waitForSelector('a[href^="/salons/"]');
await page.locator('a[href^="/salons/"]').first().click();
await page.waitForURL(/\/salons\/\d+/);
await page.waitForSelector("text=AI review summary", { timeout: 5000 }).catch(() => {});
await page.waitForTimeout(500);
await page.screenshot({ path: `${OUT}/detail.png`, fullPage: false });

await browser.close();
console.log("Saved hero.png, search.png, detail.png to docs/screenshots/");
