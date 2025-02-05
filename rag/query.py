from mojentic.llm.gateways.models import LLMMessage, MessageRole


def rag_query(llm, zk, query, chat_history):
    results = zk.query_chunks(query, n_results=10, max_distance=1.0)

    chat_history.append(
        LLMMessage(content="\n".join([result.chunk.text for result in results]) + "\n\n" + query),
    )
    result = llm.generate(chat_history, temperature=0.1)
    chat_history.append(LLMMessage(role=MessageRole.Assistant, content=result))
    return result
