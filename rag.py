from ollama import Message


def split_to_chunks(tokens, chunk_size=500, chunk_overlap=100):
    start_index = 0
    chunks = []
    while start_index < len(tokens):
        end_index = min(start_index + chunk_size, len(tokens))
        chunks.append(tokens[start_index:end_index])
        start_index += chunk_size - chunk_overlap
    return chunks


def rag_query(llm, zk, query):
    results = zk.query_chunks(query, n_results=5, max_distance=1.1)
    prompt = [
        Message(role="system", content="You are a helpful research assistant."),
        Message(role="user", content="\n".join([result.chunk.text for result in results]) + "\n\n" + query),
    ]
    return llm.generate_text(prompt, temperature=0.1)
