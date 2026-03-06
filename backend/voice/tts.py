"""
Text-to-speech via ElevenLabs using the Paddy Pimblett voice clone.
Returns MP3 bytes ready to stream to the client.

Voice settings from the spec:
    stability       0.4   — slight variation = more natural
    similarity_boost 0.85
    style           0.2
    use_speaker_boost True
"""

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from backend.config import ELEVENLABS_API_KEY, PADDY_VOICE_ID, TTS_MODEL


def synthesize(text: str) -> bytes:
    """
    Convert text to speech using the Paddy voice clone.
    Returns raw MP3 bytes.
    PADDY_VOICE_ID must be set in .env before calling this.
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    if not PADDY_VOICE_ID:
        raise RuntimeError(
            "PADDY_VOICE_ID is not set — create the voice clone in ElevenLabs "
            "and add the ID to your .env file"
        )

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    audio_chunks = client.text_to_speech.convert(
        voice_id=PADDY_VOICE_ID,
        text=text,
        model_id=TTS_MODEL,
        voice_settings=VoiceSettings(
            stability=0.4,
            similarity_boost=0.85,
            style=0.2,
            use_speaker_boost=True,
        ),
    )

    return b"".join(audio_chunks)
