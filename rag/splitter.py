def split_to_chunks(tokens, chunk_size=500, chunk_overlap=100):
    start_index = 0
    chunks = []
    while start_index < len(tokens):
        end_index = min(start_index + chunk_size, len(tokens))
        chunks.append(tokens[start_index:end_index])
        if end_index == len(tokens):
            break
        start_index += chunk_size - chunk_overlap
    return chunks
