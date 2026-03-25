# Voice AI Pipeline with KitOps & Jozu Hub

A self-hosted call centre voice agent built with open-source models, packaged and managed with [KitOps](https://kitops.ml) and [Jozu Hub](https://jozu.ml).

```
Phone → STT (Faster-Whisper) → LLM (Qwen3) → TTS (Kokoro) → Phone
```

## Why This Exists

Voice AI pipelines run **3 models updating on different schedules**. Without proper model management, you end up with:

- The wrong model version in production during a live call
- No way to roll back when a new model performs worse
- No audit trail of what's running and who deployed it

KitOps packages each model into a versioned, scannable **ModelKit**. Jozu Hub stores them with security scanning, signed attestations, and policy gates. Together, they give you `git`-like control over your AI models.

## Architecture

```
┌─────────┐     ┌──────────────────────────────────────┐     ┌─────────┐
│  Phone   │────▶│          Voice AI Pipeline            │────▶│  Phone   │
│ (caller) │ SIP │                                      │ SIP │ (caller) │
└─────────┘     │  ┌─────┐   ┌──────┐   ┌───────┐     │     └─────────┘
                │  │ STT │──▶│ LLM  │──▶│  TTS  │     │
                │  └─────┘   └──────┘   └───────┘     │
                │  Faster-    Qwen3      Kokoro        │
                │  Whisper    0.6B       82M            │
                └──────────────────────────────────────┘
                       ▲                    │
                       │    kit unpack      │
                  ┌────┴────────────────────┴────┐
                  │         Jozu Hub              │
                  │  ┌──────┐ ┌──────┐ ┌──────┐  │
                  │  │ STT  │ │ LLM  │ │ TTS  │  │
                  │  │ v1.0 │ │ v1.0 │ │ v1.0 │  │
                  │  └──────┘ └──────┘ └──────┘  │
                  └──────────────────────────────┘
```

### Models

| Role | Model | Size | Why |
|------|-------|------|-----|
| STT | Faster-Whisper Small | ~500MB | CTranslate2 backend, <200ms latency, VAD built-in |
| LLM | Qwen3-0.6B (Q4_K_M) | ~400MB | Dense model, fast CPU inference, good for scripted flows |
| TTS | Kokoro | ~300MB | 82M params, sounds better than models 10x its size |

## Quick Start

### Option A: Single `kit unpack` (demo)

```bash
# Pull the complete pipeline ModelKit
kit pull jozu.ml/voice-ai/voice-pipeline:v1.0.0

# Unpack everything — models, code, configs, prompts
kit unpack jozu.ml/voice-ai/voice-pipeline:v1.0.0 -d . -o

# Install and run
pip install -r requirements.txt
python pipeline/server.py
```

### Option B: Per-model deployment (production)

```bash
# Pull individual ModelKits
kit pull jozu.ml/voice-ai/voice-stt:v1.0.0
kit pull jozu.ml/voice-ai/voice-llm:v1.0.0
kit pull jozu.ml/voice-ai/voice-tts:v1.0.0

# Unpack only what you need
kit unpack jozu.ml/voice-ai/voice-stt:v1.0.0 -d ./models/stt --filter=model -o
kit unpack jozu.ml/voice-ai/voice-llm:v1.0.0 -d ./models/llm --filter=model --filter=prompts -o
kit unpack jozu.ml/voice-ai/voice-tts:v1.0.0 -d ./models/tts --filter=model -o

# Run
pip install -r requirements.txt
python pipeline/server.py
```

### Option C: Local development (no KitOps)

```bash
# Download models directly from Hugging Face
./scripts/setup_models.sh

# Install and run
pip install -r requirements.txt
python pipeline/server.py
```

### Docker

```bash
# Download models first
./scripts/setup_models.sh   # or kit unpack per Option B

# Run
docker compose up
```

## Testing

```bash
# Audio mode — speak into your mic
python pipeline/ws_test_client.py

# Text mode — type what the caller says
python pipeline/ws_test_client.py --text
```

## KitOps Workflow

### Packaging models

Each model has its own [Kitfile](https://kitops.ml/docs/kitfile/format/) — a YAML manifest that bundles weights, code, configs, and test data into a single OCI artifact.

```bash
# Pack individual models
kit pack ./models/stt -t jozu.ml/voice-ai/voice-stt:v1.0.0
kit pack ./models/llm -t jozu.ml/voice-ai/voice-llm:v1.0.0
kit pack ./models/tts -t jozu.ml/voice-ai/voice-tts:v1.0.0

# Push to Jozu Hub
kit push jozu.ml/voice-ai/voice-stt:v1.0.0
kit push jozu.ml/voice-ai/voice-llm:v1.0.0
kit push jozu.ml/voice-ai/voice-tts:v1.0.0
```

Or use the all-in-one script:

```bash
VERSION=v1.0.0 ./scripts/pack_and_push.sh
```

### Selective unpack

The `--filter` flag lets different roles get only what they need:

```bash
# Ops team: just the model weights (deploy to inference server)
kit unpack jozu.ml/voice-ai/voice-llm:v1.0.0 --filter=model

# Dev team: just the code and prompts (iterate on logic)
kit unpack jozu.ml/voice-ai/voice-llm:v1.0.0 --filter=code --filter=prompts

# QA team: just the test data (run validation)
kit unpack jozu.ml/voice-ai/voice-llm:v1.0.0 --filter=datasets
```

### Champion/challenger pattern

Safe model updates without downtime:

```bash
# 1. Push a new TTS model as a challenger
kit pack ./models/tts -t jozu.ml/voice-ai/voice-tts:v2.0.0
kit push jozu.ml/voice-ai/voice-tts:v2.0.0

# 2. Compare before promoting
kit diff jozu.ml/voice-ai/voice-tts:v1.0.0 jozu.ml/voice-ai/voice-tts:v2.0.0

# 3. Promote when confident
./scripts/promote_challenger.sh voice-tts v2.0.0

# 4. Roll back if needed
./scripts/rollback.sh voice-tts v1.0.0
```

### What Jozu Hub adds

When you `kit push` to Jozu Hub, your ModelKit is automatically:

- **Scanned** by 5 security scanners (ModelScan, LLM Guard, Garak, Promptfoo, ART)
- **Signed** with cryptographic attestations (via Cosign)
- **Inventoried** with an AI SBOM (SPDX 3 format)
- **Gated** by OPA policies before deployment

This means every model version in your call centre pipeline has a verifiable security and compliance record.

## Project Structure

```
jozu-voice-ai/
├── models/
│   ├── stt/
│   │   ├── Kitfile              ← STT ModelKit definition
│   │   ├── config.yaml          ← Runtime configuration
│   │   ├── src/stt_service.py   ← Faster-Whisper inference wrapper
│   │   ├── weights/             ← Model weights (via kit unpack)
│   │   └── test_data/           ← Validation audio samples
│   ├── llm/
│   │   ├── Kitfile              ← LLM ModelKit definition
│   │   ├── config.yaml
│   │   ├── src/llm_service.py   ← Qwen3 inference wrapper (llama.cpp)
│   │   ├── prompts/             ← System prompt for the agent
│   │   ├── weights/             ← Model weights (via kit unpack)
│   │   └── test_data/           ← Validation transcripts
│   └── tts/
│       ├── Kitfile              ← TTS ModelKit definition
│       ├── config.yaml
│       ├── src/tts_service.py   ← Kokoro inference wrapper
│       ├── weights/             ← Model weights (via kit unpack)
│       └── voice_profiles/      ← Voice configuration
├── pipeline/
│   ├── voice_pipeline.py        ← STT → LLM → TTS orchestration
│   ├── server.py                ← WebSocket server
│   ├── ws_test_client.py        ← Test client (mic or text input)
│   └── config.yaml
├── scripts/
│   ├── setup_models.sh          ← Download models from Hugging Face
│   ├── pack_and_push.sh         ← Pack + push all ModelKits
│   ├── deploy.sh                ← Pull + unpack on deployment target
│   ├── promote_challenger.sh    ← Promote a model version to champion
│   └── rollback.sh              ← Roll back a model to previous version
├── Kitfile                      ← Meta ModelKit (whole pipeline in one)
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── blog_outline.md
```

## Why 3 ModelKits + 1 Meta?

**3 individual ModelKits** (one per model) are the production pattern:
- Version each model independently
- Update the TTS voice without re-pushing the LLM
- Roll back just the broken model, not the whole pipeline
- Security scan results are per-model

**1 meta ModelKit** (root `Kitfile`) is the demo convenience:
- `kit unpack` once to get everything
- LLM is the `model:`, STT/TTS weights are `datasets:` (a practical trade-off since Kitfile supports one model per artifact)

## License

Apache-2.0
