#!/usr/bin/env bash
# Promote a challenger model version to champion.
#
# Usage:
#   ./scripts/promote_challenger.sh voice-tts v2.0.0
#
# This retags the specified version as :champion and deploys it.
# The previous champion is still available by its version tag for rollback.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

MODEL="${1:?Usage: promote_challenger.sh <model-name> <version>}"
VERSION="${2:?Usage: promote_challenger.sh <model-name> <version>}"
REGISTRY="${REGISTRY:-jozu.ml/voice-ai}"

# Derive local model dir from kit name (voice-stt → stt)
MODEL_DIR="${MODEL#voice-}"

if [[ ! -d "${PROJECT_ROOT}/models/${MODEL_DIR}" ]]; then
    echo "Error: models/${MODEL_DIR} does not exist. Expected one of: stt, llm, tts" >&2
    exit 1
fi

echo "=== Promoting ${MODEL}:${VERSION} to champion ==="
echo ""

echo "[1/4] Verifying ${MODEL}:${VERSION} exists..."
kit info "${REGISTRY}/${MODEL}:${VERSION}"

echo "[2/4] Tagging as :champion..."
kit tag "${REGISTRY}/${MODEL}:${VERSION}" "${REGISTRY}/${MODEL}:champion"

echo "[3/4] Pushing new champion tag..."
kit push "${REGISTRY}/${MODEL}:champion"

echo "[4/4] Deploying updated model..."
kit pull "${REGISTRY}/${MODEL}:champion"
kit unpack "${REGISTRY}/${MODEL}:champion" \
    -d "${PROJECT_ROOT}/models/${MODEL_DIR}" --filter=model -o

echo ""
echo "=== ${MODEL}:${VERSION} is now the champion ==="
echo "Restart the pipeline to pick up the new model."
