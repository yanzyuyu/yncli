#!/usr/bin/env node

const { spawn, spawnSync } = require('child_process');
const path = require('path');

function findPython() {
  const candidates = ['python3', 'python', 'py'];
  for (const cmd of candidates) {
    try {
      const res = spawnSync(cmd, ['--version'], { stdio: 'pipe', encoding: 'utf-8' });
      if (res.status === 0) {
        return cmd;
      }
    } catch (e) {
      // Continue to next candidate
    }
  }
  return null;
}

function main() {
  const pyCmd = findPython();
  if (!pyCmd) {
    console.error('\x1b[31m[ERROR] Python 3 tidak ditemukan di sistem Anda.\x1b[0m');
    console.error('Silakan install Python 3 (https://www.python.org/downloads/) untuk menjalankan yncli.');
    process.exit(1);
  }

  let targetVersion = '1.0.6';
  try {
    const pkg = require(path.join(__dirname, '..', 'package.json'));
    if (pkg && pkg.version) {
      targetVersion = pkg.version;
    }
  } catch (e) {}

  // Check installed Python yncli version (single-line, Windows-safe)
  const checkVer = spawnSync(
    pyCmd,
    ['-c', 'import yncli.version; print(yncli.version.__version__)'],
    { stdio: 'pipe', encoding: 'utf-8' }
  );
  const installedPyVer = (checkVer.status === 0 && checkVer.stdout) ? checkVer.stdout.trim() : 'none';

  if (installedPyVer !== targetVersion) {
    console.log(`\x1b[36m[YNCLI]\x1b[0m Menyinkronkan modul Python yncli ke v${targetVersion}...`);
    
    // Try exact version first
    let installRes = spawnSync(
      pyCmd,
      ['-m', 'pip', 'install', '--disable-pip-version-check', '--no-warn-script-location', '--quiet', `yncli==${targetVersion}`],
      { stdio: 'inherit' }
    );
    
    // Fallback: general upgrade if exact version not yet indexed
    if (installRes.status !== 0) {
      spawnSync(
        pyCmd,
        ['-m', 'pip', 'install', '--disable-pip-version-check', '--no-warn-script-location', '--quiet', '--upgrade', 'yncli'],
        { stdio: 'inherit' }
      );
    }
    console.log('\x1b[32m[YNCLI]\x1b[0m Sinkronisasi selesai!\n');
  }

  // Launch yncli
  const args = ['-m', 'yncli.main', ...process.argv.slice(2)];
  const child = spawn(pyCmd, args, {
    stdio: 'inherit',
    shell: false
  });

  child.on('exit', (code) => {
    process.exit(code || 0);
  });
}

main();
