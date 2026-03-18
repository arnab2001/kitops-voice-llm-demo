"""Voice AI Pipeline — orchestrates STT → LLM → TTS.

Models are loaded from local paths populated by `kit unpack`.
Run `scripts/deploy.sh` to pull and unpack models before starting.
"""

import logging
import numpy as np
import yaml
import sys
from pathlib import Path

# Add project root to path so we can import model services
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.stt.src.stt_service import STTService
from models.llm.src.llm_service import LLMService
from models.tts.src.tts_service import TTSService

logger = logging.getLogger(__name__)


class VoiceAIPipeline:
    """Orchestrates the full voice pipeline: audio in → audio out.

    Each model is loaded from paths that `kit unpack` populates.
    This decouples the pipeline code from model management — KitOps
    handles versioning, and the pipeline just reads from disk.
    """

    def __init__(self, config_path: str = None):
        config_path = Path(config_path or PROJECT_ROOT / "pipeline" / "config.yaml")
        config = self._load_config(str(config_path))

        # Resolve sub-config paths relative to this config file's directory
        config_dir = config_path.parent

        def _resolve(p: str) -> str:
            """Resolve a path relative to the config file's directory."""
            path = Path(p)
            if not path.is_absolute():
                path = (config_dir / path).resolve()
            return str(path)

        logger.info("Loading STT model (Faster-Whisper)...")
        self.stt = STTService(config_path=_resolve(config.get("stt_config", "")))

        logger.info("Loading LLM model (Qwen3)...")
        self.llm = LLMService(config_path=_resolve(config.get("llm_config", "")))

        logger.info("Loading TTS model (Kokoro)...")
        self.tts = TTSService(config_path=_resolve(config.get("tts_config", "")))

        self.tts_sample_rate = self.tts.sample_rate
        logger.info("Pipeline ready — all 3 models loaded.")

    def _load_config(self, config_path: str) -> dict:
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def process_audio(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """Full pipeline pass: caller audio → agent audio.

        Args:
            audio: Float32 numpy array of caller speech, normalized [-1.0, 1.0].
            sample_rate: Input sample rate (16kHz for Whisper).

        Returns:
            Float32 numpy array of agent response audio at self.tts_sample_rate.
        """
        # Stage 1: Speech-to-Text
        transcript = self.stt.transcribe(audio, sample_rate)
        if not transcript.strip():
            logger.debug("STT produced empty transcript, skipping.")
            return np.array([], dtype=np.float32)

        logger.info(f"[STT] Caller: {transcript}")

        # Stage 2: LLM Response
        response = self.llm.generate(transcript)
        logger.info(f"[LLM] Agent: {response}")

        # Stage 3: Text-to-Speech
        audio_out = self.tts.synthesize(response)
        logger.info(f"[TTS] Synthesized {len(audio_out)/self.tts_sample_rate:.1f}s of audio")

        return audio_out

    def process_text(self, text: str) -> np.ndarray:
        """Bypass STT — useful for testing LLM + TTS without audio input."""
        response = self.llm.generate(text)
        logger.info(f"[LLM] Agent: {response}")

        audio_out = self.tts.synthesize(response)
        logger.info(f"[TTS] Synthesized {len(audio_out)/self.tts_sample_rate:.1f}s of audio")

        return audio_out

    def reset(self):
        """Reset conversation state — call between callers."""
        self.llm.reset_conversation()
