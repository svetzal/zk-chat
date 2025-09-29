from mojentic.llm.gateways.models import LLMMessage, MessageRole


def rag_query(chat_session, zk, query):
    results = zk.query_excerpts(query, n_results=10, max_distance=1.0)

    for result in results:
        chat_session.insert_message(LLMMessage(role=MessageRole.Assistant,
                                               content=f"Excerpt from: {result.excerpt.document_title}\n"
                                                       + result.excerpt.text))

    return chat_session.send(query)
