def split_tokens(tokens: list[int], excerpt_size: int = 500, excerpt_overlap: int = 100) -> list[list[int]]:
    start_index = 0
    chunks = []
    while start_index < len(tokens):
        end_index = min(start_index + excerpt_size, len(tokens))
        chunks.append(tokens[start_index:end_index])
        if end_index == len(tokens):
            break
        start_index += excerpt_size - excerpt_overlap
    return chunks
