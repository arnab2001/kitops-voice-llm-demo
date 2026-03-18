"""Faster-Whisper STT Service for the voice AI pipeline.

Handles real-time speech-to-text transcription with VAD support,
optimized for telephony audio (8kHz/16kHz).
"""

import yaml
import numpy as np
from pathlib import Path
from faster_whisper import WhisperModel


class STTService:
    """Speech-to-text service using Faster-Whisper (CTranslate2 backend)."""

    def __init__(self, model_path: str = None, config_path: str = None):
        config, config_dir = self._load_config(config_path)
        model_path = model_path or config.get("model_path", "./weights")
        # Resolve model_path relative to config file directory
        if not Path(model_path).is_absolute():
            model_path = str((config_dir / model_path).resolve())

        self.model = WhisperModel(
            model_path,
            device=config.get("device", "cpu"),
            compute_type=config.get("compute_type", "int8"),
        )
        self.beam_size = config.get("beam_size", 3)
        self.language = config.get("language", "en")
        self.vad_filter = config.get("vad_filter", True)
        self.vad_parameters = config.get("vad_parameters", {})

    def _load_config(self, config_path: str = None) -> tuple[dict, Path]:
        path = Path(config_path or Path(__file__).parent.parent / "config.yaml")
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}, path.parent
        return {}, Path(__file__).parent.parent

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio numpy array to text.

        Args:
            audio: Float32 numpy array normalized to [-1.0, 1.0].
            sample_rate: Audio sample rate (16000 for Whisper).

        Returns:
            Full transcription as a single string.
        """
        segments, _info = self.model.transcribe(
            audio,
            beam_size=self.beam_size,
            language=self.language,
            vad_filter=self.vad_filter,
            vad_parameters=self.vad_parameters if self.vad_parameters else None,
        )
        return " ".join(seg.text.strip() for seg in segments)

    def transcribe_stream(self, audio: np.ndarray, sample_rate: int = 16000):
        """Yield transcription segments as they're produced.

        Useful for streaming partial results to the LLM before
        the full utterance is complete.
        """
        segments, _info = self.model.transcribe(
            audio,
            beam_size=self.beam_size,
            language=self.language,
            vad_filter=self.vad_filter,
            vad_parameters=self.vad_parameters if self.vad_parameters else None,
        )
        for segment in segments:
            yield segment.text.strip()
