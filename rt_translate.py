import asyncio
import base64
import json
import signal
import sys
from typing import Literal, TypedDict

import requests
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosedOK

from ui import TranscriptionWindow

GLADIA_API_URL = "https://api.gladia.io"
GLADIA_API_KEY = ""

class InitiateResponse(TypedDict):
    id: str
    url: str

class LanguageConfiguration(TypedDict):
    languages: list[str] | None
    code_switching: bool | None

class StreamingConfiguration(TypedDict):
    encoding: Literal["wav/pcm"]
    bit_depth: Literal[16]
    sample_rate: Literal[16000]
    channels: int
    language_config: LanguageConfiguration | None
    realtime_processing: dict

FFMPEG_CMD = [
    "ffmpeg", "-loglevel", "error",
    "-f", "pulse",
    "-i", "alsa_output.usb-Samsung_Samsung_USB_C_Earphones_20160406.1-00.analog-stereo.monitor",
    "-ar", "16000", "-ac", "1",
    "-f", "s16le", "-"
]

def get_gladia_key() -> str:
    return GLADIA_API_KEY

def get_streaming_config(ui: TranscriptionWindow):
    languages_map = {"Russian": "ru", "Romanian": "ro", "English": "en"}
    target = languages_map[ui.selected_lang.get()]

    return {
        "encoding": "wav/pcm",
        "bit_depth": 16,
        "sample_rate": 16000,
        "channels": 1,
        "language_config": {
            "languages": ["ru", "ro", "en"],
            "code_switching": True
        },
        "realtime_processing": {
            "translation": True,
            "translation_config": {
                "target_languages": [target]
            },
        },
    }

def init_live_session(ui: TranscriptionWindow) -> InitiateResponse:
    r = requests.post(
        f"{GLADIA_API_URL}/v2/live",
        headers={"X-Gladia-Key": get_gladia_key()},
        json=get_streaming_config(ui),
        timeout=3,
    )

    if not r.ok:
        print(f"{r.status_code}: {r.text or r.reason}", file=sys.stderr)
        sys.exit(r.status_code)
    return r.json()

async def send_audio(ws):
    """Spawn ffmpeg, read raw PCM, base64-send."""
    proc = await asyncio.create_subprocess_exec(
        *FFMPEG_CMD, stdout=asyncio.subprocess.PIPE
    )
    chunk_size = 16000 * 2 * 1 // 10
    try:
        while True:
            raw = await proc.stdout.readexactly(chunk_size)
            payload = {
                "type": "audio_chunk",
                "data": {"chunk": base64.b64encode(raw).decode()}
            }
            await ws.send(json.dumps(payload))
    except (asyncio.IncompleteReadError, ConnectionClosedOK):
        pass
    finally:
        proc.kill()

def fmt_ts(s: float) -> str:
    ms = int(s * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02}.{ms:03}"

async def translation_loop(ui: TranscriptionWindow):
    session = init_live_session(ui)
    async with connect(session["url"]) as ws:
        sender = asyncio.create_task(send_audio(ws))

        async for msg in ws:
            data = json.loads(msg)
            t = data["type"]

            if t == "transcript" and data["data"]["is_final"]:
                utt = data["data"]["utterance"]
                line = f"{fmt_ts(utt['start'])}-{fmt_ts(utt['end'])} | {utt['text'].strip()}"
                #ui.root.after(0, ui.append, line)

            elif t == "translation":
                tr = data["data"]["translated_utterance"]
                lang = data["data"]["target_language"]
                line = f"[{lang}] {tr['text'].strip()}"
                ui.root.after(0, ui.append, line)

        await sender
