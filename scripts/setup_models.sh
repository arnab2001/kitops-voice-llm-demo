#!/usr/bin/env bash
# Download model weights for local development (without KitOps).
# For production, use `kit pull` + `kit unpack` instead — see deploy.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Downloading models for local development ==="
echo ""

pip install --quiet huggingface_hub

echo "[1/3] Downloading Faster-Whisper Small (~500MB)..."
MODEL_DIR="${PROJECT_ROOT}/models/stt/weights" python3 -c "
import os
from huggingface_hub import snapshot_download
snapshot_download('Systran/faster-whisper-small', local_dir=os.environ['MODEL_DIR'])
print('  Done.')
"

echo "[2/3] Downloading Qwen3-0.6B GGUF (~400MB)..."
MODEL_DIR="${PROJECT_ROOT}/models/llm/weights" python3 -c "
import os
from huggingface_hub import hf_hub_download
hf_hub_download('Qwen/Qwen3-0.6B-GGUF', 'qwen3-0.6b-q4_k_m.gguf', local_dir=os.environ['MODEL_DIR'])
print('  Done.')
"

echo "[3/3] Downloading Kokoro TTS (~300MB)..."
MODEL_DIR="${PROJECT_ROOT}/models/tts/weights" python3 -c "
import os
from huggingface_hub import snapshot_download
snapshot_download('hexgrad/Kokoro-82M', local_dir=os.environ['MODEL_DIR'])
print('  Done.')
"

echo ""
echo "=== All models downloaded ==="
echo ""
echo "Disk usage:"
du -sh "${PROJECT_ROOT}"/models/*/weights/ 2>/dev/null || true
echo ""
echo "Next: python pipeline/server.py"
