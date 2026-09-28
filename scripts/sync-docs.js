/**
 * Copy built static CSS/icons into docs/ for GitHub Pages.
 * Leaves docs HTML, plant data, and Pages-specific JS alone.
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

ensureDir(path.join(docs, 'css'));
ensureDir(path.join(docs, 'icons'));

copyFile(path.join(root, 'static/css/app.css'), path.join(docs, 'css/app.css'));
copyFile(path.join(root, 'static/icons/icon-192.png'), path.join(docs, 'icons/icon-192.png'));
copyFile(path.join(root, 'static/icons/icon-512.png'), path.join(docs, 'icons/icon-512.png'));

console.log('docs static assets synced (CSS + icons)');
