#!/usr/bin/env bash
# Pack all ModelKits and push them to the registry.
# This is the KitOps workflow you'd run in CI/CD.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

REGISTRY="${REGISTRY:-jozu.ml/voice-ai}"
VERSION="${VERSION:-v1.0.0}"

echo "=== Packing and Pushing Voice AI ModelKits ==="
echo "Registry: ${REGISTRY}"
echo "Version:  ${VERSION}"
echo ""

# ── Pack individual ModelKits (one per model) ──────────────────────

echo "[1/8] Packing STT ModelKit..."
kit pack "${PROJECT_ROOT}/models/stt" -t "${REGISTRY}/voice-stt:${VERSION}"

echo "[2/8] Packing LLM ModelKit..."
kit pack "${PROJECT_ROOT}/models/llm" -t "${REGISTRY}/voice-llm:${VERSION}"

echo "[3/8] Packing TTS ModelKit..."
kit pack "${PROJECT_ROOT}/models/tts" -t "${REGISTRY}/voice-tts:${VERSION}"

echo "[4/8] Packing Pipeline meta-ModelKit..."
kit pack "${PROJECT_ROOT}" -t "${REGISTRY}/voice-pipeline:${VERSION}"

# ── Push to registry ───────────────────────────────────────────────

echo "[5/8] Pushing STT..."
kit push "${REGISTRY}/voice-stt:${VERSION}"

echo "[6/8] Pushing LLM..."
kit push "${REGISTRY}/voice-llm:${VERSION}"

echo "[7/8] Pushing TTS..."
kit push "${REGISTRY}/voice-tts:${VERSION}"

echo "[8/8] Pushing Pipeline meta-kit..."
kit push "${REGISTRY}/voice-pipeline:${VERSION}"

echo ""
echo "=== All ModelKits pushed ==="
echo ""
echo "Verify:"
echo "  kit list ${REGISTRY}/voice-stt"
echo "  kit list ${REGISTRY}/voice-llm"
echo "  kit list ${REGISTRY}/voice-tts"
echo "  kit list ${REGISTRY}/voice-pipeline"
echo ""
echo "Compare versions:"
echo "  kit diff ${REGISTRY}/voice-stt:v1.0.0 ${REGISTRY}/voice-stt:v2.0.0"
