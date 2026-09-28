const chokidar = require('chokidar');
const { spawn } = require('child_process');
const path = require('path');

const srcGlob = path.join(__dirname, '..', 'src', 'js', '*.js');
const buildScript = path.join(__dirname, 'build-js.js');

function rebuild() {
  const child = spawn(process.execPath, [buildScript], { stdio: 'inherit' });
  child.on('exit', (code) => {
    if (code !== 0) console.error('JS build failed');
  });
}

rebuild();
chokidar.watch(srcGlob, { ignoreInitial: true }).on('all', (event, file) => {
  console.log(`[js] ${event} ${path.basename(file)}`);
  rebuild();
});
