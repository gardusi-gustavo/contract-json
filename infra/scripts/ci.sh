#!/usr/bin/env bash
set -euo pipefail
ROOT="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
cd "$ROOT"
"$ROOT/infra/scripts/ci/validate-repo.sh" --root "$ROOT"
"$ROOT/infra/scripts/ci/check-size.sh" --root "$ROOT"
python3 scripts/validate.py --root .
while IFS= read -r f; do jq empty "$f"; done < <(find governance -type f -name '*.json' | sort)

echo "contract checks ok"
