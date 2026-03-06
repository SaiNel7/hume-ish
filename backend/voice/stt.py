"""
Speech-to-text via ElevenLabs Scribe.
Accepts raw audio bytes, returns the transcribed text.
"""

from elevenlabs.client import ElevenLabs

from backend.config import ELEVENLABS_API_KEY


def transcribe(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Send audio to ElevenLabs STT and return the transcript string.

    filename  — passed as the multipart filename so ElevenLabs can infer the
                codec. The frontend should send webm (MediaRecorder default) or
                mp3/wav. Adjust if you change the frontend recording format.
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    # file param accepts a (filename, bytes, mime_type) tuple
    mime = _mime_for(filename)
    response = client.speech_to_text.convert(
        file=(filename, audio_bytes, mime),
        model_id="scribe_v1",
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
