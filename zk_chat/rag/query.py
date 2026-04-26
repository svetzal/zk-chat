from __future__ import annotations

from typing import TYPE_CHECKING

from mojentic.llm.gateways.models import LLMMessage, MessageRole

if TYPE_CHECKING:
    from mojentic.llm import ChatSession

    from zk_chat.services.index_service import IndexService


def rag_query(chat_session: ChatSession, zk: IndexService, query: str) -> str:
    results = zk.query_excerpts(query, n_results=10, max_distance=1.0)

    for result in results:
        chat_session.insert_message(
            LLMMessage(
                role=MessageRole.Assistant,
                content=f"Excerpt from: {result.excerpt.document_title}\n" + result.excerpt.text,
            )
        )

    return chat_session.send(query)
