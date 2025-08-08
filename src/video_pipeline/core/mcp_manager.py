"""MCP Manager
================
High-level helper that starts / stops local Model Context Protocol (MCP)
servers and exposes a thin, *blocking* request interface for agents.

Currently only supports the *STDIO-based* YouTube MCP server that ships
with ``@anaisbetts/mcp-youtube``.  The full JSON-RPC framing layer is
**not** implemented yet – for now the class can:

1. Launch the child process so the server is available to ADK agents.
2. Gracefully terminate the child when the pipeline exits.

Later phases will extend ``call_tool`` to speak the MCP wire protocol and
return structured results.

Examples
--------
>>> from video_pipeline.core.mcp_manager import MCPManager
>>> mgr = MCPManager()
>>> mgr.start()          # spawns mcp-youtube under mcp_servers/
>>> # ... run pipeline ...
>>> mgr.stop()
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # cc_pipeline_v1/
MCP_BIN = (
    PROJECT_ROOT
    / "mcp_servers"
    / "node_modules"
    / ".bin"
    / ("mcp-youtube.cmd" if os.name == "nt" else "mcp-youtube")
)

def _stream_output(pipe: Any, prefix: str) -> None:
    """Drain *pipe* line-by-line so the child process doesn’t block."""
    for line in iter(pipe.readline, b""):
        try:
            decoded = line.decode().rstrip()
        except Exception:  # pragma: no cover – defensive
            decoded = str(line).rstrip()
        print(f"[MCP:{prefix}] {decoded}")
    pipe.close()


class MCPManager:
    """Simple lifecycle manager for a local STDIO MCP server."""

    def __init__(self, bin_path: Optional[Path] = None) -> None:  # noqa: D401
        self._bin_path = Path(bin_path) if bin_path else MCP_BIN
        self._proc: Optional[subprocess.Popen[bytes]] = None
        self._stderr_thread: Optional[threading.Thread] = None
        # JSON-RPC bookkeeping
        self._id_lock = threading.Lock()
        self._next_id = 1
        self._response_cond = threading.Condition()
        self._responses: dict[int, Any] = {}
        # Schema method URIs used by @modelcontextprotocol/sdk
        self._METHODS = {
            "call_tool": "tools/call",
            "list_tools": "tools/list",
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the MCP server as a background child process."""
        if self._proc and self._proc.poll() is None:
            # Already running
            return

        if not self._bin_path.exists():
            raise FileNotFoundError(
                f"Cannot find MCP binary at {self._bin_path}. "
                "Run 'bash scripts/setup_mcp_servers.sh' first."
            )

        # Spawn detached so it keeps running even if ADK spawns threads.
        self._proc = subprocess.Popen(  # noqa: S603, S607 – trusted binary
            [str(self._bin_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        # stderr is purely for diagnostics – stream it
        assert self._proc.stderr
        self._stderr_thread = threading.Thread(
            target=_stream_output, args=(self._proc.stderr, "stderr"), daemon=True
        )
        self._stderr_thread.start()

        # Start background listener thread for responses
        self._listener_thread = threading.Thread(target=self._listen_stdout, daemon=True)
        self._listener_thread.start()

        # Give the process a moment to fail fast.
        time.sleep(1)
        if self._proc.poll() is not None:
            raise RuntimeError("MCP server exited immediately – check logs above.")

    def stop(self) -> None:
        """Terminate the MCP server if running."""
        if not self._proc or self._proc.poll() is not None:
            return  # already stopped
        self._proc.terminate()
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()

    def call_tool(self, name: str, **kwargs: Any) -> Any:  # noqa: D401
        """Invoke *tool* exposed by the MCP server and return decoded result.

        This is a **blocking** helper suitable for quick calls from agents.
        It speaks the same JSON-RPC 2.0 framing as the SDK's
        ``StdioServerTransport``.  Each request and response is a single
        JSON object encoded as UTF-8 followed by a newline ("JSONL").
        """

        if not self._proc or self._proc.poll() is not None:
            raise RuntimeError("MCP server not running; call start() first")

        # ---------------- Build JSON-RPC request -------------------
        with self._id_lock:
            req_id = self._next_id
            self._next_id += 1

        request = {
            "jsonrpc": "2.0",
            "method": self._METHODS["call_tool"],
            "id": req_id,
            "params": {
                "name": name,
                "arguments": kwargs,
            },
        }

        payload = json.dumps(request, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"

        assert self._proc.stdin  # mypy
        self._proc.stdin.write(payload)
        self._proc.stdin.flush()

        # ---------------- Wait for matching response --------------
        with self._response_cond:
            self._response_cond.wait_for(lambda: req_id in self._responses, timeout=30)
            if req_id not in self._responses:
                raise TimeoutError("No response from MCP server (30s)")
            response = self._responses.pop(req_id)

        # Standard JSON-RPC error handling
        if "error" in response:
            raise RuntimeError(response["error"])

        # Some servers embed the result object directly; others wrap in "result"
        if "result" in response:
            return response["result"]
        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _listen_stdout(self) -> None:
        """Background thread decoding JSONL responses from the server."""
        assert self._proc and self._proc.stdout  # for mypy
        for raw in iter(self._proc.stdout.readline, b""):
            if not raw:
                break
            line = raw.decode(errors="replace").strip()
            if not line:
                continue
            # Optimistic parse – may fail if line is plain log text
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                print(f"[MCP:log] {line}")
                continue

            if "id" not in msg:
                # Notifications – print and ignore
                print(f"[MCP:notif] {msg}")
                continue

            with self._response_cond:
                self._responses[msg["id"]] = msg
                self._response_cond.notify_all()

        # If we exit the loop the server stdout closed – mark proc ended
        with self._response_cond:
            self._responses.clear()
            self._response_cond.notify_all()

    # ------------------------------------------------------------------
    # Context-manager helpers so callers can use ``with``
    # ------------------------------------------------------------------
    def __enter__(self) -> "MCPManager":  # noqa: D401
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: D401, ANN001 – typing
        self.stop()
        # Don’t suppress exceptions
        return False
