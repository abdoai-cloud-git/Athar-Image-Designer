#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_PATH="${REPO_ROOT}/athar_image_designer/agencii.json"

if ! command -v agencii >/dev/null 2>&1; then
  echo "The agencii CLI is required. Install it with 'pip install agencii'." >&2
  exit 1
fi

agencii deploy --config "${CONFIG_PATH}" --workflow generate_athar_image "$@"
