#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/scripts/stop.sh" --status >/dev/null 2>&1 || true
"$ROOT_DIR/scripts/stop.sh" "$@"
"$ROOT_DIR/scripts/start.sh" "$@"
