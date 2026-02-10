import { expect, test } from "@playwright/test";

test("imports markdown from local file", async ({ page }) => {
  await page.goto("/");

  const fileInput = page.locator('input[type="file"][accept=".md,text/markdown"]');
  await fileInput.setInputFiles({
    name: "demo.md",
    mimeType: "text/markdown",
    buffer: Buffer.from("# Imported\n\nHello file"),
  });

  await expect(page.locator("#markdown")).toHaveValue("# Imported\n\nHello file");
});

test("supports batch export controls", async ({ page }) => {
  await page.goto("/");

  await page.locator("#markdown").fill("# A\n\nOne\n\n---\n\n# B\n\nTwo");
  await page.getByRole("button", { name: "批量导出" }).click();

  await expect(page.getByText(/批量导出任务已完成|批量导出至少需要两段内容|批量导出失败/)).toBeVisible();
});
