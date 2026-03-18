# Voice TTS — Kokoro

Text-to-speech model for the voice AI pipeline. Uses [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), an 82M parameter model that produces remarkably natural speech.

## Model Details

| Property | Value |
|----------|-------|
| Model | Kokoro v1.0 |
| Parameters | 82M |
| Size | ~300MB |
| Output | 24kHz audio |
| Default voice | af_heart |
| Framework | PyTorch |

## KitOps Usage

```bash
# Pack
kit pack . -t jozu.ml/voice-ai/voice-tts:v1.0.0

# Push
kit push jozu.ml/voice-ai/voice-tts:v1.0.0

# Swap voice model (champion/challenger)
kit pack . -t jozu.ml/voice-ai/voice-tts:v2.0.0
kit push jozu.ml/voice-ai/voice-tts:v2.0.0
kit diff jozu.ml/voice-ai/voice-tts:v1.0.0 jozu.ml/voice-ai/voice-tts:v2.0.0
```

## Local Usage

```python
from src.tts_service import TTSService

tts = TTSService()
audio = tts.synthesize("Thank you for calling. How can I help you today?")
```
