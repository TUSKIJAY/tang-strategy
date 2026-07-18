#!/usr/bin/env bash

set -Eeuo pipefail

ACCEPTANCE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ACCEPTANCE_REPO_ROOT="$(cd "$ACCEPTANCE_SCRIPT_DIR/.." && pwd -P)"
ACCEPTANCE_HOST="127.0.0.1"
ACCEPTANCE_BACKEND_PORT="${TANG_ACCEPTANCE_BACKEND_PORT:-8000}"
ACCEPTANCE_FRONTEND_PORT="${TANG_ACCEPTANCE_FRONTEND_PORT:-5173}"
ACCEPTANCE_PYTHON="$ACCEPTANCE_REPO_ROOT/backend/.venv/bin/python"
ACCEPTANCE_UVICORN="$ACCEPTANCE_REPO_ROOT/backend/.venv/bin/uvicorn"
ACCEPTANCE_TRACKED_DB="$ACCEPTANCE_REPO_ROOT/data/sqlite/tang_strategy_live_extended.db"
ACCEPTANCE_VITE="$ACCEPTANCE_REPO_ROOT/frontend/node_modules/.bin/vite"
ACCEPTANCE_TEMP_DIR=""
ACCEPTANCE_TEMP_DB=""
ACCEPTANCE_TRACKED_SHA_BEFORE=""
ACCEPTANCE_BACKEND_PID=""
ACCEPTANCE_FRONTEND_PID=""

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

require_executable() {
  [[ -x "$1" ]] || fail "$2 is missing or not executable: $1"
}

validate_port() {
  case "$1" in
    ""|*[!0-9]*) fail "$2 must be an integer between 1 and 65535: $1" ;;
  esac
  [[ "$1" -ge 1 && "$1" -le 65535 ]] || fail "$2 must be between 1 and 65535: $1"
}

port_is_free() {
  "$ACCEPTANCE_PYTHON" - "$ACCEPTANCE_HOST" "$1" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind((host, port))
        probe.listen()
    except OSError:
        raise SystemExit(1)
PY
}

require_free_port() {
  local acceptance_port="$1"
  local acceptance_label="$2"
  if port_is_free "$acceptance_port"; then
    return
  fi
  echo "ERROR: $acceptance_label port $ACCEPTANCE_HOST:$acceptance_port is already in use; no process was stopped." >&2
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$acceptance_port" -sTCP:LISTEN >&2 || true
  fi
  exit 1
}

sha256_file() {
  "$ACCEPTANCE_PYTHON" - "$1" <<'PY'
import hashlib
import pathlib
import sys

digest = hashlib.sha256()
with pathlib.Path(sys.argv[1]).open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
print(digest.hexdigest())
PY
}

process_group_is_alive() {
  [[ -n "$1" ]] && kill -0 "-$1" 2>/dev/null
}

stop_process_group() {
  local acceptance_pid="$1"
  local acceptance_label="$2"
  local shutdown_attempt
  [[ -n "$acceptance_pid" ]] || return 0
  if process_group_is_alive "$acceptance_pid"; then
    echo "Stopping $acceptance_label process group $acceptance_pid..."
    kill -TERM "-$acceptance_pid" 2>/dev/null || true
    for shutdown_attempt in 1 2 3 4 5 6 7 8 9 10; do
      process_group_is_alive "$acceptance_pid" || break
      sleep 0.2
    done
    if process_group_is_alive "$acceptance_pid"; then
      kill -KILL "-$acceptance_pid" 2>/dev/null || true
    fi
  fi
  wait "$acceptance_pid" 2>/dev/null || true
}

cleanup() {
  local acceptance_status="$?"
  local acceptance_tracked_sha_after=""
  set +e
  trap - EXIT
  trap '' INT TERM
  stop_process_group "$ACCEPTANCE_FRONTEND_PID" "frontend"
  stop_process_group "$ACCEPTANCE_BACKEND_PID" "backend"
  if [[ -n "$ACCEPTANCE_TRACKED_SHA_BEFORE" ]]; then
    acceptance_tracked_sha_after="$(sha256_file "$ACCEPTANCE_TRACKED_DB")"
    if [[ "$acceptance_tracked_sha_after" != "$ACCEPTANCE_TRACKED_SHA_BEFORE" ]]; then
      echo "ERROR: tracked DB SHA-256 changed during local acceptance." >&2
      echo "  before: $ACCEPTANCE_TRACKED_SHA_BEFORE" >&2
      echo "  after:  $acceptance_tracked_sha_after" >&2
      acceptance_status=1
    else
      echo "Tracked DB SHA-256 unchanged: $acceptance_tracked_sha_after"
    fi
  fi
  if [[ -n "$ACCEPTANCE_TEMP_DIR" && -d "$ACCEPTANCE_TEMP_DIR" ]]; then
    rm -r -- "$ACCEPTANCE_TEMP_DIR"
    echo "Removed temporary directory: $ACCEPTANCE_TEMP_DIR"
  fi
  exit "$acceptance_status"
}

wait_for_http_200() {
  local acceptance_url="$1"
  local acceptance_label="$2"
  local acceptance_attempt
  for acceptance_attempt in {1..100}; do
    if "$ACCEPTANCE_PYTHON" - "$acceptance_url" <<'PY' >/dev/null 2>&1
import sys
import urllib.request

try:
    with urllib.request.urlopen(sys.argv[1], timeout=0.5) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
    then
      return 0
    fi
    if ! process_group_is_alive "$ACCEPTANCE_BACKEND_PID" || ! process_group_is_alive "$ACCEPTANCE_FRONTEND_PID"; then
      fail "$acceptance_label failed because an acceptance service exited during startup"
    fi
    sleep 0.2
  done
  fail "$acceptance_label did not return HTTP 200 within 20 seconds: $acceptance_url"
}

wait_for_process_group() {
  local acceptance_pid="$1"
  local acceptance_label="$2"
  local acceptance_attempt
  for acceptance_attempt in {1..40}; do
    if process_group_is_alive "$acceptance_pid"; then
      return 0
    fi
    if ! kill -0 "$acceptance_pid" 2>/dev/null; then
      fail "$acceptance_label process exited before creating its process group"
    fi
    sleep 0.05
  done
  fail "$acceptance_label process group was not created"
}

start_process_group() {
  "$ACCEPTANCE_PYTHON" - "$@" <<'PY' &
import os
import sys

os.setsid()
os.execvpe(sys.argv[1], sys.argv[1:], os.environ)
PY
  ACCEPTANCE_STARTED_PID=$!
}

cd "$ACCEPTANCE_REPO_ROOT"

require_executable "$ACCEPTANCE_PYTHON" "Backend Python runtime"
require_executable "$ACCEPTANCE_UVICORN" "Backend uvicorn runtime"
require_executable "$ACCEPTANCE_VITE" "Frontend Vite dependency"
command -v node >/dev/null 2>&1 || fail "Node.js is not available on PATH"
command -v npm >/dev/null 2>&1 || fail "npm is not available on PATH"
[[ -f "$ACCEPTANCE_TRACKED_DB" ]] || fail "Tracked SQLite DB is missing: $ACCEPTANCE_TRACKED_DB"
[[ -f "$ACCEPTANCE_REPO_ROOT/frontend/package.json" ]] || fail "frontend/package.json is missing"
npm --prefix frontend ls --depth=0 >/dev/null 2>&1 || fail "Frontend Node dependencies are incomplete; run npm install in frontend"
validate_port "$ACCEPTANCE_BACKEND_PORT" "Backend port"
validate_port "$ACCEPTANCE_FRONTEND_PORT" "Frontend port"
[[ "$ACCEPTANCE_BACKEND_PORT" != "$ACCEPTANCE_FRONTEND_PORT" ]] || fail "Backend and frontend ports must differ"
require_free_port "$ACCEPTANCE_BACKEND_PORT" "Backend"
require_free_port "$ACCEPTANCE_FRONTEND_PORT" "Frontend"

ACCEPTANCE_TRACKED_SHA_BEFORE="$(sha256_file "$ACCEPTANCE_TRACKED_DB")"
ACCEPTANCE_TEMP_DIR="$(mktemp -d "/tmp/tang-local-acceptance.XXXXXX")"
ACCEPTANCE_TEMP_DB="$ACCEPTANCE_TEMP_DIR/tang_strategy_live_extended.db"
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

"$ACCEPTANCE_PYTHON" - "$ACCEPTANCE_TRACKED_DB" "$ACCEPTANCE_TEMP_DB" <<'PY'
import contextlib
import pathlib
import sqlite3
import sys
from urllib.parse import quote

source_path = pathlib.Path(sys.argv[1]).resolve()
snapshot_path = pathlib.Path(sys.argv[2]).absolute()
source_uri = f"file:{quote(str(source_path), safe='/')}?mode=ro"
with contextlib.closing(sqlite3.connect(source_uri, uri=True)) as source:
    with contextlib.closing(sqlite3.connect(snapshot_path)) as snapshot:
        source.backup(snapshot)
        snapshot.commit()
        integrity = snapshot.execute("PRAGMA integrity_check").fetchone()[0]
        market_days = snapshot.execute("SELECT COUNT(*) FROM market_days").fetchone()[0]
if integrity != "ok":
    raise SystemExit(f"Temporary DB integrity_check failed: {integrity}")
print(f"Temporary DB: {snapshot_path}")
print(f"Snapshot market days: {market_days}")
print(f"Snapshot integrity_check: {integrity}")
PY

echo "Repository root: $ACCEPTANCE_REPO_ROOT"
echo "Tracked DB SHA-256 before startup: $ACCEPTANCE_TRACKED_SHA_BEFORE"

PYTHONPATH=backend \
TANG_DB_PATH="$ACCEPTANCE_TEMP_DB" \
start_process_group \
  "$ACCEPTANCE_UVICORN" app.main:app \
  --host "$ACCEPTANCE_HOST" --port "$ACCEPTANCE_BACKEND_PORT"
ACCEPTANCE_BACKEND_PID="$ACCEPTANCE_STARTED_PID"
wait_for_process_group "$ACCEPTANCE_BACKEND_PID" "Backend"

TANG_API_PROXY_TARGET="http://$ACCEPTANCE_HOST:$ACCEPTANCE_BACKEND_PORT" \
start_process_group \
  "$(command -v npm)" --prefix frontend run dev -- \
  --host "$ACCEPTANCE_HOST" --port "$ACCEPTANCE_FRONTEND_PORT" --strictPort
ACCEPTANCE_FRONTEND_PID="$ACCEPTANCE_STARTED_PID"
wait_for_process_group "$ACCEPTANCE_FRONTEND_PID" "Frontend"

ACCEPTANCE_BACKEND_URL="http://$ACCEPTANCE_HOST:$ACCEPTANCE_BACKEND_PORT"
ACCEPTANCE_FRONTEND_URL="http://$ACCEPTANCE_HOST:$ACCEPTANCE_FRONTEND_PORT"
wait_for_http_200 "$ACCEPTANCE_BACKEND_URL/openapi.json" "Backend OpenAPI"
wait_for_http_200 "$ACCEPTANCE_FRONTEND_URL/" "Frontend"

echo "Local acceptance services are ready:"
echo "  Frontend: $ACCEPTANCE_FRONTEND_URL/"
echo "  Backend OpenAPI: $ACCEPTANCE_BACKEND_URL/openapi.json"
echo "  Temporary DB: $ACCEPTANCE_TEMP_DB"
echo "Press Ctrl-C to stop only these services and remove the temporary directory."

while process_group_is_alive "$ACCEPTANCE_BACKEND_PID" && process_group_is_alive "$ACCEPTANCE_FRONTEND_PID"; do
  sleep 1
done
fail "An acceptance service exited unexpectedly"
