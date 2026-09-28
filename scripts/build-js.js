const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, '..', 'src', 'js');
const outDir = path.join(__dirname, '..', 'static', 'js');

fs.mkdirSync(outDir, { recursive: true });

const entries = fs.readdirSync(srcDir).filter((f) => f.endsWith('.js'));
if (!entries.length) {
  console.log('No JS entry files in src/js');
  process.exit(0);
}

esbuild
  .build({
    entryPoints: entries.map((f) => path.join(srcDir, f)),
    outdir: outDir,
    bundle: false,
    minify: true,
    target: ['es2018'],
  })
  .then(() => console.log(`Built ${entries.length} JS file(s) → static/js/`))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
