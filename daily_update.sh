#!/bin/bash
# Daily documentation update script for multiple projects
# Usage: ./daily_update.sh [--dry-run] [--force] [--filter repo1,repo2]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  . "$SCRIPT_DIR/.env"
  set +a
fi

# Default values (can be overridden by .env or CLI args)
ROOT="${GITHUB_ROOT:-$HOME/github}"
MAX_DEPTH="${TASKILL_MAX_DEPTH:-2}"
MAX_PROJECTS="${TASKILL_MAX_PROJECTS:-0}"
DRY_RUN="${TASKILL_DRY_RUN:-false}"
FORCE="${TASKILL_FORCE:-false}"
FILTER="${TASKILL_FILTER:-}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --filter)
      FILTER="$2"
      shift 2
      ;;
    --max-depth)
      MAX_DEPTH="$2"
      shift 2
      ;;
    --max-projects)
      MAX_PROJECTS="$2"
      shift 2
      ;;
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if command -v taskill >/dev/null 2>&1; then
  CMD=(taskill bulk-run)
else
  export PYTHONPATH="$SCRIPT_DIR/src:${PYTHONPATH:-}"
  CMD=(python3 -m taskill.cli bulk-run)
fi

CMD+=(--root "$ROOT" --max-depth "$MAX_DEPTH")

if [ "$MAX_PROJECTS" -gt 0 ]; then
  CMD+=(--max-projects "$MAX_PROJECTS")
fi

if [ "$DRY_RUN" = true ]; then
  CMD+=(--dry-run)
fi

if [ "$FORCE" = true ]; then
  CMD+=(--force)
fi

if [ -n "$FILTER" ]; then
  IFS=',' read -ra FILTERS <<< "$FILTER"
  for f in "${FILTERS[@]}"; do
    CMD+=(--filter "$f")
  done
fi

printf 'Running:'
printf ' %q' "${CMD[@]}"
printf '\n'
echo "========================================"

"${CMD[@]}"

echo "========================================"
echo "Done. Check ~/.taskill.log for details."
