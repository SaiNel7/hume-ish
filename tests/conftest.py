"""
Set required env vars before any backend module is imported.
The actual values don't matter — every API call is mocked in tests.
"""
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-openai")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("CARTESIA_API_KEY", "test-cartesia-key")
os.environ.setdefault("CARTESIA_VOICE_ID", "test-voice-id")
os.environ.setdefault("CHROMA_PERSIST_DIR", "/tmp/test-chroma")
