def split_tokens(tokens, excerpt_size=500, excerpt_overlap=100):
    start_index = 0
    chunks = []
    while start_index < len(tokens):
        end_index = min(start_index + excerpt_size, len(tokens))
        chunks.append(tokens[start_index:end_index])
        if end_index == len(tokens):
            break
        start_index += excerpt_size - excerpt_overlap
    return chunks
