import { test, expect } from '@playwright/test';

test('landing renders core sections', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await expect(page.getByRole('heading', { name: 'AI 报告排版助手' })).toBeVisible();
  await expect(page.getByLabel('Markdown 输入')).toBeVisible();
  await expect(page.getByRole('button', { name: '生成 Word' })).toBeVisible();
});

test('settings panel includes paragraph spacing and indent controls', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await expect(page.getByLabel('标题段前')).toBeVisible();
  await expect(page.getByLabel('标题段后')).toBeVisible();
  await expect(page.getByLabel('正文段前')).toBeVisible();
  await expect(page.getByLabel('正文段后')).toBeVisible();
  await expect(page.getByLabel('文本之前')).toBeVisible();
  await expect(page.getByLabel('文本之后')).toBeVisible();
  await expect(page.getByLabel('首行缩进')).toBeVisible();
  await expect(page.getByLabel('正文行距')).toBeVisible();
});
