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
