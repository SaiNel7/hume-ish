"""
Speech-to-text via OpenAI Whisper.
Accepts raw audio bytes, returns the transcribed text.
"""

import io

from openai import OpenAI

from backend.config import OPENAI_API_KEY


def transcribe(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Send audio to OpenAI Whisper and return the transcript string.

    filename  — used to infer the codec. The frontend should send webm
                (MediaRecorder default) or mp3/wav. Adjust if you change
                the frontend recording format.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename

    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )

    return response.text


def _mime_for(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "webm": "audio/webm",
        "mp3":  "audio/mpeg",
        "wav":  "audio/wav",
        "ogg":  "audio/ogg",
        "m4a":  "audio/mp4",
    }.get(ext, "application/octet-stream")
