"""
Text-to-speech via Cartesia using the Paddy Pimblett voice clone.
Returns MP3 bytes ready to stream to the client.
"""

from cartesia import Cartesia

from backend.config import CARTESIA_API_KEY, CARTESIA_VOICE_ID, TTS_MODEL


def synthesize(text: str) -> bytes:
    """
    Convert text to speech using the Paddy voice clone.
    Returns raw MP3 bytes.
    CARTESIA_VOICE_ID must be set in .env before calling this.
    """
    if not CARTESIA_API_KEY:
        raise RuntimeError("CARTESIA_API_KEY is not set")
    if not CARTESIA_VOICE_ID:
        raise RuntimeError(
            "CARTESIA_VOICE_ID is not set — create the voice clone in Cartesia "
            "and add the ID to your .env file"
        )

    client = Cartesia(api_key=CARTESIA_API_KEY)

    chunks = client.tts.bytes(
        model_id=TTS_MODEL,
        transcript=text,
        voice={"id": CARTESIA_VOICE_ID},
        output_format={
            "container": "mp3",
            "bit_rate": 128000,
            "sample_rate": 44100,
        },
    )

    return b"".join(chunks)
