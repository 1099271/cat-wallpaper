#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
API_PID_FILE="$RUN_DIR/api.pid"
WEB_PID_FILE="$RUN_DIR/web.pid"

mkdir -p "$RUN_DIR"

usage() {
  cat <<'EOF'
Usage: ./scripts/start.sh [--api] [--web] [--all] [--status]

Options:
  --api   Start API only
  --web   Start Web only
  --all     Start both (default)
  --status  Show running status and exit
EOF
}

START_API=false
START_WEB=false
STATUS_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api)
      START_API=true
      ;;
    --web)
      START_WEB=true
      ;;
    --all)
      START_API=true
      START_WEB=true
      ;;
    --status)
      STATUS_ONLY=true
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

if [[ "$STATUS_ONLY" == "true" ]]; then
  if is_running "$API_PID_FILE"; then
    echo "API running (pid $(cat "$API_PID_FILE"))."
  else
    echo "API not running."
  fi
  if is_running "$WEB_PID_FILE"; then
    echo "Web running (pid $(cat "$WEB_PID_FILE"))."
  else
    echo "Web not running."
  fi
  exit 0
fi

if [[ "$START_API" == "false" && "$START_WEB" == "false" ]]; then
  START_API=true
  START_WEB=true
fi

is_running() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if ps -p "$pid" >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

ensure_env_file() {
  local target="$1"
  local example="$2"
  if [[ ! -f "$target" ]]; then
    cp "$example" "$target"
    echo "Created $target from example. Please edit it."
  fi
}

start_api() {
  if is_running "$API_PID_FILE"; then
    echo "API already running (pid $(cat "$API_PID_FILE"))."
    return
  fi

  ensure_env_file "$ROOT_DIR/apps/api/.env" "$ROOT_DIR/apps/api/.env.example"

  pushd "$ROOT_DIR/apps/api" >/dev/null
  if [[ ! -d ".venv" ]]; then
    uv venv .venv
  fi
  uv pip install -e '.[dev]'

  nohup .venv/bin/uvicorn app.main:app --reload --port 8000 \
    > "$RUN_DIR/api.log" 2>&1 &
  echo $! > "$API_PID_FILE"
  popd >/dev/null

  echo "API started (pid $(cat "$API_PID_FILE"))."
}

start_web() {
  if is_running "$WEB_PID_FILE"; then
    echo "Web already running (pid $(cat "$WEB_PID_FILE"))."
    return
  fi

  ensure_env_file "$ROOT_DIR/apps/web/.env" "$ROOT_DIR/apps/web/.env.example"

  pushd "$ROOT_DIR" >/dev/null
  if [[ ! -d "node_modules" ]]; then
    pnpm install
  fi

  nohup pnpm --filter web dev -- --port 3000 \
    > "$RUN_DIR/web.log" 2>&1 &
  echo $! > "$WEB_PID_FILE"
  popd >/dev/null

  echo "Web started (pid $(cat "$WEB_PID_FILE"))."
}

if [[ "$START_API" == "true" ]]; then
  start_api
fi

if [[ "$START_WEB" == "true" ]]; then
  start_web
fi

echo "Logs: $RUN_DIR/api.log, $RUN_DIR/web.log"
