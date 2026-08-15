#!/usr/bin/env bash
# Run the three eval prompts through opencode run and check each CSV.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="${EVAL_MODEL:-opencode-go/hy3}"
RUNS="$ROOT/eval/runs"
mkdir -p "$RUNS"

echo "model=$MODEL"

for spec in 01-starter 02-careful 03-precise; do
  dest="$RUNS/$spec"
  mkdir -p "$dest"
  rm -f "$ROOT/claim.csv"
  echo "===== $spec ====="
  # opencode run is the headless equivalent of claude -p.
  # --auto is required so the agent can write claim.csv.
  opencode run --auto \
    --dir "$ROOT" \
    --model "$MODEL" \
    --title "claims-eval-$spec" \
    "$(cat "$ROOT/eval/$spec.txt")" \
    | tee "$dest/opencode.log"
  if [[ -f "$ROOT/claim.csv" ]]; then
    cp "$ROOT/claim.csv" "$dest/claim.csv"
    python3 "$ROOT/check.py" --csv-file "$dest/claim.csv" \
      >"$dest/check.txt" 2>&1 || true
    echo "check:"
    cat "$dest/check.txt"
  else
    echo "NO_CLAIM_CSV" | tee "$dest/check.txt"
  fi
done

echo "done. results in $RUNS"
