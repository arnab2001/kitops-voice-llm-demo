"""WebSocket test client for the voice AI pipeline.

Two modes:
  1. Audio mode (default): Records from mic, sends to pipeline, plays response.
  2. Text mode (--text): Type messages, hear the agent's spoken response.

Usage:
  python ws_test_client.py              # Audio mode
  python ws_test_client.py --text       # Text mode (no mic needed)
"""

import argparse
import asyncio
import json
import numpy as np
import websockets

SAMPLE_RATE_IN = 16000
RECORD_SECONDS = 5
WS_URL = "ws://localhost:8765"


async def audio_mode():
    """Record from mic → send to pipeline → play response."""
    import sounddevice as sd

    print(f"Connecting to {WS_URL}...")
    async with websockets.connect(WS_URL) as ws:
        print("Connected. Audio mode — speak into your mic.\n")

        while True:
            input(f"Press Enter to record {RECORD_SECONDS}s (Ctrl+C to quit)...")

            print("  Recording...")
            audio = sd.rec(
                int(RECORD_SECONDS * SAMPLE_RATE_IN),
                samplerate=SAMPLE_RATE_IN,
                channels=1,
                dtype="int16",
            )
            sd.wait()
            print("  Sending to pipeline...")

            await ws.send(audio.tobytes())

            response = await ws.recv()
            response_audio = np.frombuffer(response, dtype=np.int16)

            duration = len(response_audio) / 24000  # TTS outputs at 24kHz
            print(f"  Playing response ({duration:.1f}s)...")
            sd.play(response_audio, samplerate=24000)
            sd.wait()


async def text_mode():
    """Type text → send to pipeline → play spoken response."""
    import sounddevice as sd

    print(f"Connecting to {WS_URL}...")
    async with websockets.connect(WS_URL) as ws:
        print("Connected. Text mode — type what the caller says.\n")

        while True:
            text = input("Caller: ").strip()
            if not text:
                continue

            await ws.send(json.dumps({"type": "text", "content": text}))

            response = await ws.recv()
            response_audio = np.frombuffer(response, dtype=np.int16)

            duration = len(response_audio) / 24000
            print(f"  Agent responds ({duration:.1f}s audio)...")
            sd.play(response_audio, samplerate=24000)
            sd.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice AI pipeline test client")
    parser.add_argument("--text", action="store_true", help="Text mode (no mic)")
    parser.add_argument("--url", default=WS_URL, help="WebSocket URL")
    args = parser.parse_args()

    WS_URL = args.url

    try:
        if args.text:
            asyncio.run(text_mode())
        else:
            asyncio.run(audio_mode())
    except KeyboardInterrupt:
        print("\nDone.")
