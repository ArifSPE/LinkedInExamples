#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_DIR="$SCRIPT_DIR/.pids"

if [[ -x "$SCRIPT_DIR/../.venv/bin/python" ]]; then
  PYTHON_BIN="$SCRIPT_DIR/../.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

mkdir -p "$LOG_DIR" "$PID_DIR"

API_LOG="$LOG_DIR/api.log"
MCP_LOG="$LOG_DIR/mcpserver.log"
API_PID_FILE="$PID_DIR/api.pid"
MCP_PID_FILE="$PID_DIR/mcpserver.pid"

is_running() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

start_service() {
  local name="$1"
  local cmd="$2"
  local log_file="$3"
  local pid_file="$4"

  if is_running "$pid_file"; then
    local pid
    pid="$(cat "$pid_file")"
    echo "$name is already running (PID: $pid)"
    return
  fi

  echo "Starting $name..."
  # Use exec so the recorded PID maps to the long-lived service process.
  nohup bash -lc "exec $cmd" >"$log_file" 2>&1 &
  local pid=$!
  echo "$pid" >"$pid_file"
  echo "$name started (PID: $pid)"
}

cd "$SCRIPT_DIR"

start_service "API" "\"$PYTHON_BIN\" api.py" "$API_LOG" "$API_PID_FILE"
start_service "MCP Server" "\"$PYTHON_BIN\" mcpserver.py" "$MCP_LOG" "$MCP_PID_FILE"

echo
echo "Logs:"
echo "  API: $API_LOG"
echo "  MCP: $MCP_LOG"
echo "PID files:"
echo "  API: $API_PID_FILE"
echo "  MCP: $MCP_PID_FILE"
