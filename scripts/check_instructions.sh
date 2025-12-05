#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required but not found. Install it before running this check."
  exit 1
fi

FORBIDDEN_PATTERNS=(
  "Human-readable"
  "MAIN PROMPT"
  "Please answer"
  "What do you want"
  "Explain your reasoning"
)

mapfile -t FILE_ARRAY < <(rg --files -g "*agent/instructions.md" || true)
if [[ ${#FILE_ARRAY[@]} -eq 0 ]]; then
  echo "No agent instruction files found"
  exit 0
fi

violations=0
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  matches=$(rg --with-filename --line-number --no-heading --fixed-strings "$pattern" "${FILE_ARRAY[@]}" || true)
  if [[ -n "$matches" ]]; then
    echo "Forbidden pattern '$pattern' detected in instructions:"
    echo "$matches"
    violations=1
  fi
done

if [[ $violations -ne 0 ]]; then
  echo "\nInstruction validation failed. Remove forbidden prose before committing."
  exit 1
fi

echo "Instruction files clean."
