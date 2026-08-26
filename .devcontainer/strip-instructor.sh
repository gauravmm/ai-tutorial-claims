#!/usr/bin/env bash
# Drop instructor-only files in a student Codespace. No-op on a laptop.
set -euo pipefail

if [[ "${KEEP_INSTRUCTOR:-}" == "1" ]]; then
  echo "KEEP_INSTRUCTOR=1; leaving .instructor"
  exit 0
fi

if [[ "${CODESPACES:-}" != "true" && -z "${CODESPACE_NAME:-}" ]]; then
  echo "not a GitHub Codespace; leaving .instructor"
  exit 0
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -d "$ROOT/.instructor" ]]; then
  rm -rf "$ROOT/.instructor"
  echo "removed .instructor"
fi

if [[ -d "$ROOT/dataset/display/.render" ]]; then
  rm -rf "$ROOT/dataset/display/.render"
  echo "removed dataset/display/.render"
fi

# Reset history so the stripped files never show up in the student's git view.
rm -rf "$ROOT/.git"
git -C "$ROOT" init -q -b main
git -C "$ROOT" add -A
git -C "$ROOT" -c user.name="Expense Claims" -c user.email="noreply@example.com" \
  commit -q -m "Initial commit"
echo "re-initialised git history"
