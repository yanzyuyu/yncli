#!/usr/bin/env node
const { spawnSync } = require("child_process");
const path = require("path");

// Native execution fallback - expects python on system
const args = process.argv.slice(2);
const pythonCmd = process.platform === "win32" ? "python" : "python3";
const result = spawnSync(pythonCmd, ["-m", "yncli", ...args], {
    stdio: "inherit"
});
process.exit(result.status || 0);
