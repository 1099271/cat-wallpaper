#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
API_PID_FILE="$RUN_DIR/api.pid"
WEB_PID_FILE="$RUN_DIR/web.pid"

mkdir -p "$RUN_DIR"

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

start_api
start_web

echo "Logs: $RUN_DIR/api.log, $RUN_DIR/web.log"
