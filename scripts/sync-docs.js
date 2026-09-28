/**
 * Copy built static CSS/icons/images into docs/ for GitHub Pages.
 * Leaves docs HTML, plant data, and Pages-specific JS alone —
 * except images, which are mirrored from static/ so Django and Pages stay in sync.
 */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const docs = path.join(root, 'docs');

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function copyFile(src, dest) {
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
  console.log(`synced ${path.relative(root, dest)}`);
}

function copyDir(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return;
  ensureDir(destDir);
  for (const name of fs.readdirSync(srcDir)) {
    const s = path.join(srcDir, name);
    const d = path.join(destDir, name);
    if (fs.statSync(s).isDirectory()) copyDir(s, d);
    else copyFile(s, d);
  }
}

ensureDir(path.join(docs, 'css'));
ensureDir(path.join(docs, 'icons'));
ensureDir(path.join(docs, 'images'));

copyFile(path.join(root, 'static/css/app.css'), path.join(docs, 'css/app.css'));
copyFile(path.join(root, 'static/icons/icon-192.png'), path.join(docs, 'icons/icon-192.png'));
copyFile(path.join(root, 'static/icons/icon-512.png'), path.join(docs, 'icons/icon-512.png'));
copyDir(path.join(root, 'static/images'), path.join(docs, 'images'));

console.log('docs static assets synced (CSS + icons + images)');
