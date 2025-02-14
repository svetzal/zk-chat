from zk_chat.rag.splitter import split_to_chunks

def test_split_to_chunks_exact_chunk_size():
    tokens = list(range(500))
    chunk_size = 500
    chunk_overlap = 100
    expected_chunks = [tokens]
    chunks = split_to_chunks(tokens, chunk_size, chunk_overlap)
    assert chunks == expected_chunks

def test_split_to_chunks_with_overlap():
    tokens = list(range(600))
    chunk_size = 500
    chunk_overlap = 100
    expected_chunks = [tokens[:500], tokens[400:600]]
    chunks = split_to_chunks(tokens, chunk_size, chunk_overlap)
    assert chunks == expected_chunks

def test_split_to_chunks_no_overlap():
    tokens = list(range(1000))
    chunk_size = 500
    chunk_overlap = 0
    expected_chunks = [tokens[:500], tokens[500:1000]]
    chunks = split_to_chunks(tokens, chunk_size, chunk_overlap)
    assert chunks == expected_chunks

def test_split_to_chunks_smaller_than_chunk_size():
    tokens = list(range(300))
    chunk_size = 500
    chunk_overlap = 100
    expected_chunks = [tokens]
    chunks = split_to_chunks(tokens, chunk_size, chunk_overlap)
    assert chunks == expected_chunks

def test_split_to_chunks_with_remainder():
    tokens = list(range(750))
    chunk_size = 500
    chunk_overlap = 100
    expected_chunks = [tokens[:500], tokens[400:750]]
    chunks = split_to_chunks(tokens, chunk_size, chunk_overlap)
    assert chunks == expected_chunks

def test_split_to_chunks_empty_tokens():
    tokens = []
    chunk_size = 500
    chunk_overlap = 100
    expected_chunks = []
    chunks = split_to_chunks(tokens, chunk_size, chunk_overlap)
    assert chunks == expected_chunks