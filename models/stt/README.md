# Voice STT — Faster-Whisper Small

Speech-to-text model for the voice AI pipeline. Uses [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) with the CTranslate2 backend for low-latency transcription.

## Model Details

| Property | Value |
|----------|-------|
| Base model | Whisper Small |
| Backend | CTranslate2 |
| Size | ~500MB |
| Latency | <200ms per utterance (CPU) |
| Input | 16kHz mono audio |
| VAD | Built-in (silero) |

## KitOps Usage

```bash
# Pack
kit pack . -t jozu.ml/voice-ai/voice-stt:v1.0.0

# Push
kit push jozu.ml/voice-ai/voice-stt:v1.0.0

# Unpack (model weights only)
kit unpack jozu.ml/voice-ai/voice-stt:v1.0.0 --filter=model -d ./output
```

## Local Usage

```python
from src.stt_service import STTService

stt = STTService()
text = stt.transcribe(audio_array, sample_rate=16000)
```
