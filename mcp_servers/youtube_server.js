#!/usr/bin/env node
// Launches the STDIO-based YouTube MCP server binary that ships with
// @anaisbetts/mcp-youtube. Uses absolute path into local node_modules.

const { spawn } = require('child_process');
const path = require('path');

const binPath = path.resolve(__dirname, 'node_modules', '.bin', process.platform === 'win32' ? 'mcp-youtube.cmd' : 'mcp-youtube');

console.log('[YouTube MCP] Starting STDIO server via', binPath);

const proc = spawn(binPath, [], { stdio: 'inherit' });

proc.on('error', (err) => {
  console.error('[YouTube MCP] Failed to start:', err);
  process.exit(1);
});

proc.on('exit', (code) => {
  console.log(`[YouTube MCP] Process exited with code ${code}`);
  process.exit(code);
});
