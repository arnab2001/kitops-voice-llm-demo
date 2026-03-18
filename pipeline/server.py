"""WebSocket server for the voice AI pipeline.

Accepts audio from a telephony bridge (Jambonz) or test client,
runs it through STT → LLM → TTS, and streams audio back.

Protocol:
  - Client sends: raw bytes (16-bit PCM, 16kHz mono)
  - Server sends: raw bytes (16-bit PCM, 24kHz mono)
  - Client sends: JSON {"type": "end"} to hang up
"""

import asyncio
import json
import logging
import sys
import numpy as np
import yaml
import websockets
from pathlib import Path

# Ensure project root is on sys.path so imports work regardless of CWD
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from pipeline.voice_pipeline import VoiceAIPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("voice-server")

INPUT_SAMPLE_RATE = 16000


def _encode_pcm(audio: np.ndarray) -> bytes:
    """Encode float32 audio to 16-bit PCM bytes."""
    return (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16).tobytes()


async def handle_connection(websocket, pipeline: VoiceAIPipeline):
    """Handle a single WebSocket connection (one phone call)."""
    remote = websocket.remote_address
    logger.info(f"New call connected: {remote}")
    pipeline.reset()

    loop = asyncio.get_event_loop()

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                # Decode 16-bit PCM to float32
                audio = (
                    np.frombuffer(message, dtype=np.int16).astype(np.float32) / 32768.0
                )

                # Offload blocking ML inference to a thread pool
                response_audio = await loop.run_in_executor(
                    None, pipeline.process_audio, audio, INPUT_SAMPLE_RATE
                )

                if len(response_audio) > 0:
                    await websocket.send(_encode_pcm(response_audio))

            elif isinstance(message, str):
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {remote}")
                    continue

                if data.get("type") == "end":
                    logger.info(f"Call ended by client: {remote}")
                    break
                elif data.get("type") == "text":
                    content = data.get("content", "")
                    if not content:
                        continue
                    # Text-only mode (bypass STT) for quick testing
                    response_audio = await loop.run_in_executor(
                        None, pipeline.process_text, content
                    )
                    if len(response_audio) > 0:
                        await websocket.send(_encode_pcm(response_audio))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        logger.info(f"Call disconnected: {remote}")


async def main():
    config_path = Path(__file__).parent / "config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    host = config.get("host", "0.0.0.0")
    port = config.get("port", 8765)

    logger.info("Initializing voice AI pipeline...")
    pipeline = VoiceAIPipeline()

    logger.info(f"Starting WebSocket server on ws://{host}:{port}")

    async with websockets.serve(
        lambda ws: handle_connection(ws, pipeline),
        host,
        port,
    ):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
