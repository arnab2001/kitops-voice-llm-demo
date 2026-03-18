#!/usr/bin/env bash
# Pull and unpack all models from the registry.
# This is what you run on a deployment target.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

REGISTRY="${REGISTRY:-jozu.ml/voice-ai}"
STT_TAG="${STT_TAG:-voice-stt:latest}"
LLM_TAG="${LLM_TAG:-voice-llm:latest}"
TTS_TAG="${TTS_TAG:-voice-tts:latest}"

echo "=== Deploying Voice AI Pipeline ==="
echo "Registry: ${REGISTRY}"
echo ""

echo "[1/6] Pulling STT model..."
kit pull "${REGISTRY}/${STT_TAG}"

echo "[2/6] Pulling LLM model..."
kit pull "${REGISTRY}/${LLM_TAG}"

echo "[3/6] Pulling TTS model..."
kit pull "${REGISTRY}/${TTS_TAG}"

echo "[4/6] Unpacking STT (model + code)..."
kit unpack "${REGISTRY}/${STT_TAG}" \
    -d "${PROJECT_ROOT}/models/stt" \
    --filter=model --filter=code -o

echo "[5/6] Unpacking LLM (model + code + prompts)..."
kit unpack "${REGISTRY}/${LLM_TAG}" \
    -d "${PROJECT_ROOT}/models/llm" \
    --filter=model --filter=code --filter=prompts -o

echo "[6/6] Unpacking TTS (model + code)..."
kit unpack "${REGISTRY}/${TTS_TAG}" \
    -d "${PROJECT_ROOT}/models/tts" \
    --filter=model --filter=code -o

echo ""
echo "=== All models deployed ==="
echo ""
echo "Model versions:"
kit info "${REGISTRY}/${STT_TAG}" 2>/dev/null | head -5 || true
kit info "${REGISTRY}/${LLM_TAG}" 2>/dev/null | head -5 || true
kit info "${REGISTRY}/${TTS_TAG}" 2>/dev/null | head -5 || true
echo ""
echo "Start the pipeline:"
echo "  python pipeline/server.py"
