"""Kokoro TTS Service for the voice AI pipeline.

Handles text-to-speech synthesis with multiple voice profiles,
producing 24kHz audio suitable for telephony playback.
"""

import yaml
import numpy as np
from pathlib import Path


class TTSService:
    """Text-to-speech service using Kokoro."""

    def __init__(self, model_path: str = None, config_path: str = None):
        config, config_dir = self._load_config(config_path)
        model_path = model_path or config.get("model_path", "./weights")
        # Resolve model_path relative to config file directory
        if not Path(model_path).is_absolute():
            model_path = str((config_dir / model_path).resolve())

        from kokoro import KPipeline

        self.pipeline = KPipeline(
            lang_code=config.get("lang_code", "a"),
            repo_id=model_path,
        )
        self.default_voice = config.get("default_voice", "af_heart")
        self.sample_rate = config.get("sample_rate", 24000)
        self.speed = config.get("speed", 1.0)

    def _load_config(self, config_path: str = None) -> tuple[dict, Path]:
        path = Path(config_path or Path(__file__).parent.parent / "config.yaml")
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}, path.parent
        return {}, Path(__file__).parent.parent

    def synthesize(self, text: str, voice: str = None) -> np.ndarray:
        """Convert text to a complete audio array.

        Args:
            text: Text to synthesize.
            voice: Voice profile ID (defaults to config value).

        Returns:
            Float32 numpy array of audio samples at self.sample_rate.
        """
        voice = voice or self.default_voice
        audio_chunks = []

        for _graphemes, _phonemes, audio in self.pipeline(
            text, voice=voice, speed=self.speed
        ):
            if audio is not None:
                audio_chunks.append(audio)

        if not audio_chunks:
            return np.array([], dtype=np.float32)
        return np.concatenate(audio_chunks)

    def synthesize_stream(self, text: str, voice: str = None):
        """Yield audio chunks as they're synthesized.

        Useful for streaming audio back to the caller before
        the full response is synthesized.
        """
        voice = voice or self.default_voice
        for _graphemes, _phonemes, audio in self.pipeline(
            text, voice=voice, speed=self.speed
        ):
            if audio is not None:
                yield audio
