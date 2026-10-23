"""
Voice module — Gnani STT/TTS integration (Step 4).

Gnani STT: WebSocket-based real-time speech-to-text.
Gnani TTS: REST API for text-to-speech audio streaming.

NOTE: Record your own voice to test — no pre-recorded audio files are supplied.
Replace placeholder API keys and endpoints with real Gnani credentials.
"""

import asyncio
import os
import json
import websockets
import httpx

GNANI_STT_WS_URL = os.getenv("GNANI_STT_WS_URL", "wss://api.gnani.ai/stt/v1/stream")
GNANI_TTS_URL = os.getenv("GNANI_TTS_URL", "https://api.gnani.ai/tts/v1/synthesize")
GNANI_API_KEY = os.getenv("GNANI_API_KEY", "")


async def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """
    Send raw audio bytes to Gnani STT over WebSocket and return the transcript.

    Args:
        audio_bytes: PCM 16kHz mono audio bytes (or WAV).
        language: ISO language code ('en', 'hi', 'hi-en', etc.)

    Returns:
        Transcribed text string.
    """
    headers = {"Authorization": f"Bearer {GNANI_API_KEY}"}
    transcript_parts = []

    async with websockets.connect(GNANI_STT_WS_URL, extra_headers=headers) as ws:
        # Send config frame
        config = {"language": language, "sample_rate": 16000, "encoding": "LINEAR16"}
        await ws.send(json.dumps(config))

        # Stream audio in chunks
        chunk_size = 4096
        for i in range(0, len(audio_bytes), chunk_size):
            await ws.send(audio_bytes[i: i + chunk_size])

        # Signal end of stream
        await ws.send(json.dumps({"eof": True}))

        # Collect results
        async for message in ws:
            result = json.loads(message)
            if result.get("is_final"):
                transcript_parts.append(result.get("transcript", ""))
            if result.get("end_of_utterance"):
                break

    return " ".join(transcript_parts).strip()


async def synthesize_speech(text: str, language: str = "en") -> bytes:
    """
    Convert text to speech using Gnani TTS and return raw audio bytes.

    Args:
        text: Text to synthesize.
        language: ISO language code.

    Returns:
        Audio bytes (WAV or MP3, depending on Gnani config).
    """
    headers = {
        "Authorization": f"Bearer {GNANI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "language": language,
        "voice": "female",
        "sample_rate": 16000,
        "format": "wav",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GNANI_TTS_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.content


# ── Convenience sync wrappers ──────────────────────────────────────────────────

def stt(audio_bytes: bytes, language: str = "en") -> str:
    """Synchronous wrapper for transcribe_audio."""
    return asyncio.run(transcribe_audio(audio_bytes, language))


def tts(text: str, language: str = "en") -> bytes:
    """Synchronous wrapper for synthesize_speech."""
    return asyncio.run(synthesize_speech(text, language))
