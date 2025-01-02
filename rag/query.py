from ollama import Message


def rag_query(llm, zk, query):
    results = zk.query_chunks(query, n_results=5, max_distance=1.1)
    prompt = [
        Message(role="system", content="You are a helpful research assistant."),
        Message(role="user", content="\n".join([result.chunk.text for result in results]) + "\n\n" + query),
    ]
    return llm.generate_text(prompt, temperature=0.1)
