# MCP Server Setup Guide

This document explains how to install and configure **Model Context Protocol (MCP)** servers for the AI Video Essay Pipeline. We start with a **YouTube MCP server** that surfaces YouTube Data API functionality (search, video metadata, etc.) to agents.

---

## 1. Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Node.js      | ≥ 18.x | Needed for running the MCP server package. |
| npm / pnpm   | Latest | Package manager for installing `@anaisbetts/mcp-youtube`. |
| Python       | ≥ 3.10 | The pipeline itself. |
| YouTube API Key | N/A | Generated from [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com). |

> ℹ️ If you do not have Node.js, the helper script `scripts/setup_mcp_servers.sh` installs **nvm** and the required Node version.

---

## 2. Environment Variables

Copy `.env.example` to `.env` and fill in **`YOUTUBE_API_KEY`**.

```
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `YOUTUBE_API_KEY` | **Required.** Google YouTube Data v3 API key. |
| `YOUTUBE_MCP_PORT` | Optional. Port for the local server (default `5010`). |

---

## 3. Automated Setup (Recommended)

Run the helper script:

```bash
bash scripts/setup_mcp_servers.sh
```

The script will:

1. Verify Node.js ≥ 18 is available (installs via **nvm** if missing).
2. Install the YouTube MCP package locally:
   ```bash
   npm install --prefix mcp_servers @anaisbetts/mcp-youtube
   ```
3. Generate `mcp_servers/youtube_server.js` – a thin wrapper that launches the STDIO-based server.
4. Run the server:
   ```bash
   node mcp_servers/youtube_server.js   # stays silent; Ctrl-C to stop
   ```

---

## 4. Manual Installation (Optional)

```bash
# Inside project root
cd mcp_servers
npm init -y
npm install @anaisbetts/mcp-youtube --save
```

Create `youtube_server.js`:

```js
// Thin wrapper – place in mcp_servers/youtube_server.js
const { spawn } = require('child_process');
const path = require('path');
const bin = path.resolve(__dirname, 'node_modules', '.bin', process.platform === 'win32' ? 'mcp-youtube.cmd' : 'mcp-youtube');
spawn(bin, { stdio: 'inherit' });
```

Then run:

```bash
node youtube_server.js   # or use the generated wrapper
```

---

## 5. Docker-Compose (Alternative) – *TBD*

---

## 6. Health Checks & Logs

* This server uses **STDIO transport**, so there is no HTTP health endpoint.
* Successful start = no error output. Use `ps` or `pgrep mcp-youtube` to confirm.
* Logs are written to `mcp_servers/logs/youtube_mcp.log` by default. Rotate or tail as needed.

---

## 7. Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `Error: API key invalid` | Ensure `YOUTUBE_API_KEY` is correct and unrestricted (or add referer/IP rules). |
| Port already in use | Change `YOUTUBE_MCP_PORT` in `.env` or stop the conflicting service. |
| `node: command not found` | Install Node.js via `nvm`, Homebrew, or official installer. |

---

## 8. Next Steps

With the server running you can now proceed to **Phase 2 (MCP Client Infrastructure)** and implement the Python-side `MCPManager` for connecting agents to this server.
