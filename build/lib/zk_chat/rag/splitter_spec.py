from zk_chat.rag.splitter import split_tokens


class DescribeSplitter:
    def should_keep_tokens_as_single_chunk_when_equal_to_chunk_size(self):
        tokens = list(range(500))
        chunk_size = 500
        chunk_overlap = 100
        expected_chunks = [tokens]
        chunks = split_tokens(tokens, chunk_size, chunk_overlap)
        assert chunks == expected_chunks

    def should_split_tokens_with_specified_overlap(self):
        tokens = list(range(600))
        chunk_size = 500
        chunk_overlap = 100
        expected_chunks = [tokens[:500], tokens[400:600]]
        chunks = split_tokens(tokens, chunk_size, chunk_overlap)
        assert chunks == expected_chunks

    def should_split_tokens_without_overlap(self):
        tokens = list(range(1000))
        chunk_size = 500
        chunk_overlap = 0
        expected_chunks = [tokens[:500], tokens[500:1000]]
        chunks = split_tokens(tokens, chunk_size, chunk_overlap)
        assert chunks == expected_chunks

    def should_keep_tokens_as_single_chunk_when_smaller_than_chunk_size(self):
        tokens = list(range(300))
        chunk_size = 500
        chunk_overlap = 100
        expected_chunks = [tokens]
        chunks = split_tokens(tokens, chunk_size, chunk_overlap)
        assert chunks == expected_chunks

    def should_handle_remainder_tokens_in_last_chunk(self):
        tokens = list(range(750))
        chunk_size = 500
        chunk_overlap = 100
        expected_chunks = [tokens[:500], tokens[400:750]]
        chunks = split_tokens(tokens, chunk_size, chunk_overlap)
        assert chunks == expected_chunks

    def should_return_empty_list_for_empty_input(self):
        tokens = []
        chunk_size = 500
        chunk_overlap = 100
        expected_chunks = []
        chunks = split_tokens(tokens, chunk_size, chunk_overlap)
        assert chunks == expected_chunks
