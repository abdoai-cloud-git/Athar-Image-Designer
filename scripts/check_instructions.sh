#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATTERN='Human-readable|MAIN PROMPT|Please answer|What do you want|Explain'

echo "Scanning agent instructions for forbidden prose..."
matches="$(grep -EnR --include='instructions.md' --exclude-dir='.git' -e "${PATTERN}" "${ROOT_DIR}" || true)"

if [[ -n "${matches}" ]]; then
  echo "Found forbidden prose usage:"
  echo "${matches}"
  exit 1
fi

echo "Instructions are clean."
