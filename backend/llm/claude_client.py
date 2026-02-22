"""
Claude API wrapper for generating Hume's responses.
"""

import anthropic
from backend.config import ANTHROPIC_API_KEY, LLM_MODEL
from backend.llm.prompts import HUME_SYSTEM_PROMPT

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_response(conversation_history: list[dict], rag_context: str) -> str:
    """
    Send conversation_history + RAG context to Claude and return the reply text.
    conversation_history: list of {"role": "user"|"assistant", "content": str}
    """
    system = HUME_SYSTEM_PROMPT.format(rag_context=rag_context)
    response = _client.messages.create(
        model=LLM_MODEL,
        max_tokens=300,
        system=system,
        messages=conversation_history,
    )
    return response.content[0].text
