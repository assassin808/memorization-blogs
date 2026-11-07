// Renders video-40s/index.html to a 1920x1080, 30 fps MP4 with soundtrack.mp3 muxed in.
// Usage: node video-40s/tools/export.js [out.mp4]
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');

(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.resolve(process.argv[2] || path.join(root, 'gss-explainer.mp4'));
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'gss-'));
  const page_html = path.join(tmp, 'page.html');
  fs.writeFileSync(page_html, '<!doctype html><html><head><meta charset="utf-8"></head><body>' +
    fs.readFileSync(path.join(root, 'index.html'), 'utf8') + '</body></html>');

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1.2 });
  await page.goto('file://' + page_html + '?export');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);

  const D = await page.evaluate(() => window.__duration);
  const FPS = 30, N = Math.round(D * FPS);
  for (let i = 0; i < N; i++) {
    await page.evaluate((x) => window.__renderAt(x), i / FPS);
    await page.screenshot({ path: path.join(tmp, `f${String(i).padStart(4, '0')}.png`) });
  }
  await browser.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(tmp, 'f%04d.png'),
    '-i', path.join(root, 'soundtrack.mp3'), '-map', '0:v', '-map', '1:a', '-shortest',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('wrote', out);
})();
