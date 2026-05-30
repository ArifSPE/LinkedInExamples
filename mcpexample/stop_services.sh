#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"

API_PID_FILE="$PID_DIR/api.pid"
MCP_PID_FILE="$PID_DIR/mcpserver.pid"

stop_pid() {
  local name="$1"
  local pid="$2"

  if ! kill -0 "$pid" 2>/dev/null; then
    return 1
  fi

  echo "Stopping $name (PID: $pid)..."
  kill "$pid"

  # Wait briefly for graceful shutdown before forcing.
  for _ in {1..10}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.5
  done

  if kill -0 "$pid" 2>/dev/null; then
    echo "$name did not stop gracefully, forcing stop"
    kill -9 "$pid"
  fi

  echo "$name stopped"
  return 0
}

stop_by_pattern() {
  local name="$1"
  local pattern="$2"
  local pids

  pids="$(pgrep -f "$pattern" || true)"
  if [[ -z "$pids" ]]; then
    return 1
  fi

  while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    stop_pid "$name" "$pid" || true
  done <<< "$pids"

  return 0
}

stop_service() {
  local name="$1"
  local pid_file="$2"
  local pattern="$3"
  local stopped=0

  if [[ ! -f "$pid_file" ]]; then
    if stop_by_pattern "$name" "$pattern"; then
      stopped=1
    else
      echo "$name is not running (no PID file found)"
    fi
  else
    local pid
    pid="$(cat "$pid_file")"

    if [[ -n "$pid" ]] && stop_pid "$name" "$pid"; then
      stopped=1
    else
      if [[ -n "$pid" ]]; then
        echo "$name has stale PID file entry: $pid"
      else
        echo "$name has an empty PID file"
      fi

      if stop_by_pattern "$name" "$pattern"; then
        stopped=1
      fi
    fi
  fi

  rm -f "$pid_file"

  if [[ "$stopped" -eq 0 ]]; then
    echo "$name is not running"
  fi
}

stop_service "API" "$API_PID_FILE" "api.py"
stop_service "MCP Server" "$MCP_PID_FILE" "mcpserver.py"
