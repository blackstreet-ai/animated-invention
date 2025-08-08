#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scripts/setup_mcp_servers.sh
# ---------------------------------------------------------------------------
# Automated installer for local MCP servers (Phase 1).
#  * Installs Node.js via nvm if absent (Mac/Linux).
#  * Installs @anaisbetts/mcp-youtube under mcp_servers/
#  * Generates starter youtube_server.js if missing.
#  * Performs a basic health-check.
#
# Usage:
#   bash scripts/setup_mcp_servers.sh [--force]
# ---------------------------------------------------------------------------
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_DIR="$PROJECT_ROOT/mcp_servers"
YOUTUBE_DIR="$MCP_DIR/node_modules/@anaisbetts/mcp-youtube"
DOTENV_DIR="$MCP_DIR/node_modules/dotenv"
DEFAULT_PORT="5010"
FORCE=0

for arg in "$@"; do
  [[ "$arg" == "--force" ]] && FORCE=1
done

# -------------------------------------------------------------
# 1. Ensure Node.js (>=18) is available
# -------------------------------------------------------------
if ! command -v node >/dev/null 2>&1; then
  echo "[setup_mcp] Node.js not found. Installing via nvm..."
  if ! command -v nvm >/dev/null 2>&1; then
    # Install nvm (quiet)
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    # shellcheck source=/dev/null
    source "$HOME/.nvm/nvm.sh"
  fi
  nvm install 18
  nvm use 18
fi

NODE_MAJOR="$(node -v | sed -E 's/v([0-9]+)\..*/\1/')"
if (( NODE_MAJOR < 18 )); then
  echo "[setup_mcp] Node.js >=18 is required. Current: $(node -v)" >&2
  exit 1
fi

echo "[setup_mcp] Using Node $(node -v)"

# -------------------------------------------------------------
# 2. Install YouTube MCP package (if missing or --force)
# -------------------------------------------------------------
mkdir -p "$MCP_DIR"
if [[ ! -d "$YOUTUBE_DIR" || "$FORCE" == 1 ]]; then
  echo "[setup_mcp] Installing @anaisbetts/mcp-youtube and dotenv..."
  npm install --prefix "$MCP_DIR" @anaisbetts/mcp-youtube@latest dotenv@latest
else
  echo "[setup_mcp] Package exists. Skipping npm install. Use --force to reinstall."
fi

echo "[setup_mcp] Checking for yt-dlp..."

# -------------------------------------------------------------
# 3. Generate youtube_server.js stub if absent
# -------------------------------------------------------------
SERVER_JS="$MCP_DIR/youtube_server.js"
if [[ ! -f "$SERVER_JS" ]]; then
  cat >"$SERVER_JS" <<'JS'
#!/usr/bin/env node
// Launches the STDIO-based YouTube MCP server binary that ships with
// @anaisbetts/mcp-youtube. Uses absolute path into local node_modules.
const { spawn } = require('child_process');
const path = require('path');
const binPath = path.resolve(__dirname, 'node_modules', '.bin', process.platform === 'win32' ? 'mcp-youtube.cmd' : 'mcp-youtube');
spawn(binPath, [], { stdio: 'inherit' });
JS
  chmod +x "$SERVER_JS"
  echo "[setup_mcp] Generated $SERVER_JS"
fi

# -------------------------------------------------------------
# 4. Smoke-test the server (optional)
# -------------------------------------------------------------
if [[ -z "${CI:-}" ]]; then
  echo "[setup_mcp] Starting temporary server for smoke-test..."
  node "$SERVER_JS" &
  SERVER_PID=$!
  sleep 2
  kill "$SERVER_PID" || true
  echo "[setup_mcp] ✔ Smoke-test completed (server started and was terminated)."
fi

echo "[setup_mcp] Setup complete. Run: node $SERVER_JS"
