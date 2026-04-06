from zk_chat.chroma_collections import ZkCollectionName


class DescribeZkCollectionName:
    """Tests for the ZkCollectionName enum."""

    def should_have_excerpts_member(self):
        assert ZkCollectionName.EXCERPTS is not None

    def should_have_documents_member(self):
        assert ZkCollectionName.DOCUMENTS is not None

    def should_have_zettelkasten_member(self):
        assert ZkCollectionName.ZETTELKASTEN is not None

    def should_have_smart_memory_member(self):
        assert ZkCollectionName.SMART_MEMORY is not None

    def should_have_exactly_four_members(self):
        assert len(ZkCollectionName) == 4

    class DescribeStr:
        """Tests for the __str__ method."""

        def should_convert_excerpts_to_string(self):
            assert str(ZkCollectionName.EXCERPTS) == "excerpts"

        def should_convert_documents_to_string(self):
            assert str(ZkCollectionName.DOCUMENTS) == "documents"

        def should_convert_zettelkasten_to_string(self):
            assert str(ZkCollectionName.ZETTELKASTEN) == "zettelkasten"

        def should_convert_smart_memory_to_string(self):
            assert str(ZkCollectionName.SMART_MEMORY) == "smart_memory"
