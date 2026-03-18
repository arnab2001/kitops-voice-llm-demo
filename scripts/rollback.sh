#!/usr/bin/env bash
# Roll back a model to a previous version.
#
# Usage:
#   ./scripts/rollback.sh voice-stt v1.0.0
#
# Pulls the specified version, unpacks it, and retags as :champion.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

MODEL="${1:?Usage: rollback.sh <model-name> <version>}"
VERSION="${2:?Usage: rollback.sh <model-name> <version>}"
REGISTRY="${REGISTRY:-jozu.ml/voice-ai}"

MODEL_DIR="${MODEL#voice-}"

if [[ ! -d "${PROJECT_ROOT}/models/${MODEL_DIR}" ]]; then
    echo "Error: models/${MODEL_DIR} does not exist. Expected one of: stt, llm, tts" >&2
    exit 1
fi

echo "=== Rolling back ${MODEL} to ${VERSION} ==="
echo ""

echo "[1/4] Pulling ${MODEL}:${VERSION}..."
kit pull "${REGISTRY}/${MODEL}:${VERSION}"

echo "[2/4] Unpacking model weights..."
kit unpack "${REGISTRY}/${MODEL}:${VERSION}" \
    -d "${PROJECT_ROOT}/models/${MODEL_DIR}" --filter=model -o

echo "[3/4] Updating champion tag..."
kit tag "${REGISTRY}/${MODEL}:${VERSION}" "${REGISTRY}/${MODEL}:champion"

echo "[4/4] Pushing updated champion tag..."
kit push "${REGISTRY}/${MODEL}:champion"

echo ""
echo "=== Rolled back ${MODEL} to ${VERSION} ==="
echo "Restart the pipeline to pick up the rolled-back model."
