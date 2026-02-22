"""
Speech-to-text via ElevenLabs /speech-to-text endpoint.
Accepts raw audio bytes and returns the transcribed text.
"""


def transcribe(audio_bytes: bytes) -> str:
    """Send audio to ElevenLabs STT and return transcript."""
    raise NotImplementedError
