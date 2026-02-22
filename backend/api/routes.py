"""
FastAPI routes for the Ask Hume voice pipeline.

POST /chat/text   — text in, text out (useful for testing without voice)
POST /chat/voice  — audio in, audio out (full pipeline)
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/chat/text")
async def chat_text():
    raise NotImplementedError


@router.post("/chat/voice")
async def chat_voice():
    raise NotImplementedError
