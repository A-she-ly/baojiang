"""
TTS Proxy Server
================
Provides text-to-speech audio via HTTP API.

- Spanish (es): Microsoft Edge TTS (neural voices, high quality)
- English (en): Youdao Dict Voice API

Endpoints:
  GET /api/tts?text=Hello&lang=en
  GET /api/tts?text=Hola&lang=es

Run:
  python scripts/tts_proxy.py
  # Listens on http://localhost:8901
"""

from __future__ import annotations
import asyncio
import sys
from pathlib import Path

try:
    from aiohttp import web
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Run: pip install aiohttp", file=sys.stderr)
    sys.exit(1)

try:
    import edge_tts
except ImportError:
    edge_tts = None
    print("WARNING: edge-tts not installed. Spanish TTS unavailable. Run: pip install edge-tts")


# ---------------------------------------------------------------------------
# Edge TTS (Spanish)
# ---------------------------------------------------------------------------
EDGE_VOICE_ES = "es-ES-AlvaroNeural"  # Male Spanish voice
EDGE_VOICE_EN = "en-US-GuyNeural"     # Male English voice (fallback)

# Default output format (MP3, 24kHz)
EDGE_FORMAT = "audio-24khz-48kbitrate-mono-mp3"


async def edge_tts_stream(text: str, voice: str = EDGE_VOICE_ES) -> bytes:
    """Generate TTS audio using Edge TTS and return raw bytes."""
    if edge_tts is None:
        raise RuntimeError("edge-tts is not installed")

    communicate = edge_tts.Communicate(text, voice, rate="+0%", volume="+0%", pitch="+0Hz")
    audio_chunks: list[bytes] = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])

    return b"".join(audio_chunks)


# ---------------------------------------------------------------------------
# Youdao Dict Voice (English fallback)
# ---------------------------------------------------------------------------
YOUDAO_URL = "https://dict.youdao.com/dictvoice"


async def youdao_tts_stream(text: str, tts_type: int = 2) -> bytes:
    """Fetch TTS audio from Youdao Dict Voice API."""
    async with aiohttp.ClientSession() as session:
        params = {"type": str(tts_type), "audio": text}
        async with session.get(YOUDAO_URL, params=params) as resp:
            if resp.status == 200:
                return await resp.read()
            raise RuntimeError(f"Youdao TTS returned status {resp.status}")


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------
async def handle_tts(request: web.Request) -> web.Response:
    """
    GET /api/tts?text=<url-encoded-text>&lang=<es|en>
    """
    text = request.query.get("text", "").strip()
    lang = request.query.get("lang", "es").strip().lower()
    tts_type = request.query.get("type", "2").strip()

    if not text:
        return web.Response(text="Missing 'text' parameter", status=400)

    try:
        if lang == "es":
            # Use Edge TTS for Spanish
            audio_data = await edge_tts_stream(text, EDGE_VOICE_ES)
            content_type = "audio/mpeg"
        elif lang == "en":
            # Use Youdao for English (original behavior)
            audio_data = await youdao_tts_stream(text, int(tts_type))
            content_type = "audio/mpeg"
        else:
            # Default to Edge TTS with English voice
            audio_data = await edge_tts_stream(text, EDGE_VOICE_EN)
            content_type = "audio/mpeg"

        return web.Response(
            body=audio_data,
            content_type=content_type,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=86400",
            },
        )
    except Exception as e:
        print(f"[TTS ERROR] lang={lang}, text={text[:50]}... -> {e}", file=sys.stderr)
        return web.Response(text=str(e), status=500)


# ---------------------------------------------------------------------------
# CORS preflight
# ---------------------------------------------------------------------------
async def handle_options(request: web.Request) -> web.Response:
    return web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    port = 8901
    app = web.Application()
    app.router.add_get("/api/tts", handle_tts)
    app.router.add_options("/api/tts", handle_options)

    print(f"🔊 TTS Proxy Server starting on http://localhost:{port}")
    print(f"   Spanish → Edge TTS ({EDGE_VOICE_ES})")
    print(f"   English → Youdao Dict Voice")
    print(f"   Endpoint: GET /api/tts?text=<text>&lang=<es|en>")

    if edge_tts is None:
        print("   ⚠️  edge-tts NOT installed — Spanish TTS unavailable!")
        print("   Install with: pip install edge-tts")

    web.run_app(app, host="0.0.0.0", port=port, print=None)


if __name__ == "__main__":
    main()
