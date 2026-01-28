#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
API_PID_FILE="$RUN_DIR/api.pid"
WEB_PID_FILE="$RUN_DIR/web.pid"

usage() {
  cat <<'EOF'
Usage: ./scripts/stop.sh [--api] [--web] [--all]

Options:
  --api   Stop API only
  --web   Stop Web only
  --all   Stop both (default)
EOF
}

STOP_API=false
STOP_WEB=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api)
      STOP_API=true
      ;;
    --web)
      STOP_WEB=true
      ;;
    --all)
      STOP_API=true
      STOP_WEB=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ "$STOP_API" == "false" && "$STOP_WEB" == "false" ]]; then
  STOP_API=true
  STOP_WEB=true
fi

stop_process() {
  local name="$1"
  local pid_file="$2"
  if [[ ! -f "$pid_file" ]]; then
    echo "$name not running (no pid file)."
    return
  fi

  local pid
  pid="$(cat "$pid_file")"
  if ps -p "$pid" >/dev/null 2>&1; then
    kill "$pid" || true
    sleep 1
    if ps -p "$pid" >/dev/null 2>&1; then
      kill -9 "$pid" || true
    fi
    echo "$name stopped."
  else
    echo "$name not running (stale pid)."
  fi

  rm -f "$pid_file"
}

if [[ "$STOP_API" == "true" ]]; then
  stop_process "API" "$API_PID_FILE"
fi

if [[ "$STOP_WEB" == "true" ]]; then
  stop_process "Web" "$WEB_PID_FILE"
fi
