from unittest.mock import Mock, patch
from datetime import datetime

import pytest

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway, WikiLink
from zk_chat.services.link_traversal_service import (
    LinkTraversalService,
    WikiLinkReference,
    BacklinkResult,
    ForwardLinkResult,
    LinkPath,
    LinkMetrics,
    LinkGraphIndex
)


class DescribeLinkTraversalService:
    """
    Tests for the LinkTraversalService which handles wikilink analysis and graph traversal.
    """

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def link_service(self, mock_filesystem):
        return LinkTraversalService(mock_filesystem)

    @pytest.fixture
    def sample_content_with_links(self):
        return """# Sample Document

This document contains several wikilinks:
- Reference to [[Document A]]
- Link with caption [[Document B|Display Name]]
- Another link to [[Document C]] in the same line.

Some content without links.

Final reference to [[Document A]] again.
"""

    @pytest.fixture
    def sample_content_no_links(self):
        return """# Document Without Links

This document has no wikilinks at all.
Just plain markdown content.
"""

    def should_be_instantiated_with_filesystem_gateway(self, mock_filesystem):
        service = LinkTraversalService(mock_filesystem)

        assert isinstance(service, LinkTraversalService)
        assert service.filesystem_gateway == mock_filesystem
        assert isinstance(service.link_index, LinkGraphIndex)

    def should_extract_wikilinks_from_content_with_context(self, link_service, sample_content_with_links):
        source_document = "test.md"

        result = link_service.extract_wikilinks_from_content(sample_content_with_links, source_document)

        assert len(result) == 4  # Four wikilinks total

        # Check first wikilink
        first_link = result[0]
        assert first_link.wikilink.title == "Document A"
        assert first_link.wikilink.caption is None
        assert first_link.line_number == 4
        assert first_link.source_document == source_document
        assert "Reference to [[Document A]]" in first_link.context_snippet

        # Check link with caption
        caption_link = result[1]
        assert caption_link.wikilink.title == "Document B"
        assert caption_link.wikilink.caption == "Display Name"
        assert caption_link.line_number == 5

        # Check that duplicate links are found
        duplicate_link = result[3]
        assert duplicate_link.wikilink.title == "Document A"
        assert duplicate_link.line_number == 10

    def should_extract_wikilinks_from_document_file(self, link_service, mock_filesystem, sample_content_with_links):
        test_path = "test/document.md"
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({}, sample_content_with_links)

        result = link_service.extract_wikilinks_from_document(test_path)

        mock_filesystem.path_exists.assert_called_once_with(test_path)
        mock_filesystem.read_markdown.assert_called_once_with(test_path)
        assert len(result) == 4
        assert all(ref.source_document == test_path for ref in result)

    def should_return_empty_list_for_nonexistent_document(self, link_service, mock_filesystem):
        test_path = "nonexistent.md"
        mock_filesystem.path_exists.return_value = False

        result = link_service.extract_wikilinks_from_document(test_path)

        assert result == []

    def should_handle_content_with_no_wikilinks(self, link_service, sample_content_no_links):
        result = link_service.extract_wikilinks_from_content(sample_content_no_links, "test.md")

        assert result == []

    def should_skip_malformed_wikilinks(self, link_service):
        content_with_malformed = """Valid: [[Good Link]]
Invalid: [[Bad Link Missing Bracket
Another valid: [[Another Good Link]]"""

        result = link_service.extract_wikilinks_from_content(content_with_malformed, "test.md")

        assert len(result) == 2
        assert result[0].wikilink.title == "Good Link"
        assert result[1].wikilink.title == "Another Good Link"

    def should_find_backlinks_using_index_when_available(self, link_service, mock_filesystem):
        # Setup mock index with backlinks
        target_doc = "target.md"
        linking_doc = "linking.md"

        # Create a wikilink reference
        wikilink_ref = WikiLinkReference(
            wikilink=WikiLink(title="target", caption=None),
            line_number=5,
            context_snippet="Link to [[target]]",
            source_document=linking_doc
        )

        # Setup the index
        link_service.link_index.backward_links[target_doc] = {linking_doc}
        link_service.link_index.wikilink_references[linking_doc] = [wikilink_ref]

        result = link_service.find_backlinks(target_doc)

        assert len(result) == 1
        backlink = result[0]
        assert backlink.linking_document == linking_doc
        assert backlink.resolved_target == target_doc
        assert backlink.line_number == 5

    def should_find_backlinks_by_scanning_when_index_unavailable(self, link_service, mock_filesystem):
        target_doc = "target.md"
        linking_doc = "linking.md"

        # Mock filesystem iteration
        mock_filesystem.iterate_markdown_files.return_value = [linking_doc]
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({}, "Link to [[target]] here")
        mock_filesystem.resolve_wikilink.return_value = target_doc

        result = link_service.find_backlinks(target_doc)

        assert len(result) == 1
        backlink = result[0]
        assert backlink.linking_document == linking_doc
        assert backlink.resolved_target == target_doc

    def should_find_forward_links_from_document(self, link_service, mock_filesystem):
        source_doc = "source.md"
        target_doc = "target.md"

        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({}, "Link to [[target]]")
        mock_filesystem.resolve_wikilink.return_value = target_doc

        result = link_service.find_forward_links(source_doc)

        assert len(result) == 1
        forward_link = result[0]
        assert forward_link.source_document == source_doc
        assert forward_link.resolved_target == target_doc
        assert forward_link.target_wikilink == "[[target]]"

    def should_handle_broken_forward_links(self, link_service, mock_filesystem):
        source_doc = "source.md"

        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({}, "Link to [[nonexistent]]")
        mock_filesystem.resolve_wikilink.side_effect = ValueError("Not found")

        result = link_service.find_forward_links(source_doc)

        assert len(result) == 1
        forward_link = result[0]
        assert forward_link.source_document == source_doc
        assert forward_link.resolved_target is None  # Broken link
        assert forward_link.target_wikilink == "[[nonexistent]]"

    def should_build_link_index_from_all_documents(self, link_service, mock_filesystem):
        # Mock filesystem with two documents
        doc1 = "doc1.md"
        doc2 = "doc2.md"

        mock_filesystem.iterate_markdown_files.return_value = [doc1, doc2]
        mock_filesystem.path_exists.return_value = True

        # doc1 links to doc2
        mock_filesystem.read_markdown.side_effect = [
            ({}, "Link to [[doc2]]"),  # doc1 content
            ({}, "No links here")      # doc2 content
        ]

        # Resolve wikilink from doc1 to doc2
        mock_filesystem.resolve_wikilink.return_value = doc2

        link_service.build_link_index()

        # Check forward links
        assert doc2 in link_service.link_index.get_forward_links(doc1)
        assert len(link_service.link_index.get_forward_links(doc2)) == 0

        # Check backward links
        assert doc1 in link_service.link_index.get_backward_links(doc2)
        assert len(link_service.link_index.get_backward_links(doc1)) == 0

        assert link_service.link_index.last_updated is not None

    def should_find_link_path_between_documents(self, link_service, mock_filesystem):
        # Setup a simple path: doc1 -> doc2 -> doc3
        doc1, doc2, doc3 = "doc1.md", "doc2.md", "doc3.md"

        # Build the index manually for testing
        link_service.link_index.forward_links = {
            doc1: {doc2},
            doc2: {doc3},
            doc3: set()
        }
        link_service.link_index.last_updated = datetime.now()

        result = link_service.find_link_path(doc1, doc3, max_hops=3)

        assert result is not None
        assert result.from_document == doc1
        assert result.to_document == doc3
        assert result.path == [doc1, doc2, doc3]
        assert result.hops == 2

    def should_return_none_when_no_path_exists(self, link_service, mock_filesystem):
        # Setup disconnected documents
        doc1, doc2 = "doc1.md", "doc2.md"

        link_service.link_index.forward_links = {
            doc1: set(),
            doc2: set()
        }
        link_service.link_index.last_updated = datetime.now()

        result = link_service.find_link_path(doc1, doc2, max_hops=3)

        assert result is None

    def should_respect_max_hops_limit(self, link_service, mock_filesystem):
        # Setup a long chain: doc1 -> doc2 -> doc3 -> doc4
        doc1, doc2, doc3, doc4 = "doc1.md", "doc2.md", "doc3.md", "doc4.md"

        link_service.link_index.forward_links = {
            doc1: {doc2},
            doc2: {doc3},
            doc3: {doc4},
            doc4: set()
        }
        link_service.link_index.last_updated = datetime.now()

        # Should find path with enough hops
        result = link_service.find_link_path(doc1, doc4, max_hops=3)
        assert result is not None
        assert result.hops == 3

        # Should not find path with insufficient hops
        result = link_service.find_link_path(doc1, doc4, max_hops=2)
        assert result is None

    def should_calculate_global_link_metrics(self, link_service, mock_filesystem):
        # Setup test index with known structure
        doc1, doc2, doc3 = "doc1.md", "doc2.md", "doc3.md"

        link_service.link_index.forward_links = {
            doc1: {doc2},      # doc1 links to doc2
            doc2: {doc3},      # doc2 links to doc3
            doc3: set()        # doc3 has no outgoing links
        }

        link_service.link_index.backward_links = {
            doc1: set(),       # doc1 has no incoming links (orphaned)
            doc2: {doc1},      # doc2 is linked by doc1
            doc3: {doc2}       # doc3 is linked by doc2
        }

        link_service.link_index.broken_links = {
            doc1: {"broken1"},
            doc2: set(),
            doc3: {"broken2", "broken3"}
        }

        link_service.link_index.last_updated = datetime.now()

        metrics = link_service.get_link_metrics()

        assert metrics.total_documents == 3
        assert metrics.total_links == 2  # doc1->doc2, doc2->doc3
        assert metrics.total_broken_links == 3  # broken1, broken2, broken3
        assert doc1 in metrics.orphaned_documents  # doc1 has no incoming links
        assert metrics.average_links_per_document == 2.0 / 3.0

        # Check hub documents (most incoming links)
        hub_documents = dict(metrics.hub_documents)
        assert hub_documents[doc2] == 1  # doc2 has 1 incoming link
        assert hub_documents[doc3] == 1  # doc3 has 1 incoming link

    def should_calculate_document_specific_metrics(self, link_service, mock_filesystem):
        doc1 = "doc1.md"

        link_service.link_index.forward_links = {doc1: {"doc2.md", "doc3.md"}}
        link_service.link_index.backward_links = {doc1: {"source.md"}}
        link_service.link_index.broken_links = {doc1: {"broken.md"}}
        link_service.link_index.last_updated = datetime.now()

        metrics = link_service.get_link_metrics(doc1)

        assert metrics.total_documents == 1
        assert metrics.total_links == 2  # Forward links
        assert metrics.total_broken_links == 1
        assert metrics.average_links_per_document == 2.0
        assert metrics.hub_documents == [(doc1, 1)]  # 1 incoming link

    def should_create_proper_context_snippets(self, link_service):
        line = "This is a long line with a [[Test Link]] in the middle of some other content"
        start = line.index("[[Test Link]]")
        end = start + len("[[Test Link]]")

        snippet = link_service._create_context_snippet(line, start, end, context_chars=20)

        assert "[[Test Link]]" in snippet
        assert "long line with a" in snippet
        assert "in the middle of" in snippet

    def should_truncate_long_context_with_ellipses(self, link_service):
        long_prefix = "a" * 100
        long_suffix = "b" * 100
        line = f"{long_prefix} [[Test Link]] {long_suffix}"
        start = line.index("[[Test Link]]")
        end = start + len("[[Test Link]]")

        snippet = link_service._create_context_snippet(line, start, end, context_chars=10)

        assert snippet.startswith("...")
        assert snippet.endswith("...")
        assert "[[Test Link]]" in snippet


class DescribeLinkGraphIndex:
    """
    Tests for the LinkGraphIndex class which maintains the in-memory link graph.
    """

    @pytest.fixture
    def link_index(self):
        return LinkGraphIndex()

    @pytest.fixture
    def sample_wikilink_ref(self):
        return WikiLinkReference(
            wikilink=WikiLink(title="target", caption=None),
            line_number=1,
            context_snippet="[[target]]",
            source_document="source.md"
        )

    def should_be_instantiated_with_empty_collections(self, link_index):
        assert isinstance(link_index.forward_links, dict)
        assert isinstance(link_index.backward_links, dict)
        assert isinstance(link_index.broken_links, dict)
        assert isinstance(link_index.wikilink_references, dict)
        assert link_index.last_updated is None

    def should_add_document_links_correctly(self, link_index, sample_wikilink_ref):
        source_doc = "source.md"
        target_doc = "target.md"
        resolved_targets = {"target": target_doc}

        link_index.add_document_links(source_doc, [sample_wikilink_ref], resolved_targets)

        assert target_doc in link_index.get_forward_links(source_doc)
        assert source_doc in link_index.get_backward_links(target_doc)
        assert len(link_index.get_broken_links(source_doc)) == 0

    def should_handle_broken_links(self, link_index, sample_wikilink_ref):
        source_doc = "source.md"
        resolved_targets = {"target": None}  # Broken link

        link_index.add_document_links(source_doc, [sample_wikilink_ref], resolved_targets)

        assert len(link_index.get_forward_links(source_doc)) == 0
        assert "target" in link_index.get_broken_links(source_doc)

    def should_update_existing_document_links(self, link_index):
        source_doc = "source.md"
        old_target = "old_target.md"
        new_target = "new_target.md"

        # Add initial link
        old_ref = WikiLinkReference(
            wikilink=WikiLink(title="old_target", caption=None),
            line_number=1,
            context_snippet="[[old_target]]",
            source_document=source_doc
        )
        link_index.add_document_links(source_doc, [old_ref], {"old_target": old_target})

        # Update with new link
        new_ref = WikiLinkReference(
            wikilink=WikiLink(title="new_target", caption=None),
            line_number=1,
            context_snippet="[[new_target]]",
            source_document=source_doc
        )
        link_index.add_document_links(source_doc, [new_ref], {"new_target": new_target})

        # Old link should be removed, new link should be present
        assert old_target not in link_index.get_forward_links(source_doc)
        assert new_target in link_index.get_forward_links(source_doc)
        assert source_doc not in link_index.get_backward_links(old_target)
        assert source_doc in link_index.get_backward_links(new_target)

    def should_find_direct_path(self, link_index):
        doc1, doc2 = "doc1.md", "doc2.md"
        link_index.forward_links = {doc1: {doc2}}

        path = link_index.find_path(doc1, doc2)

        assert path is not None
        assert path.path == [doc1, doc2]
        assert path.hops == 1

    def should_find_multi_hop_path(self, link_index):
        doc1, doc2, doc3 = "doc1.md", "doc2.md", "doc3.md"
        link_index.forward_links = {
            doc1: {doc2},
            doc2: {doc3},
            doc3: set()
        }

        path = link_index.find_path(doc1, doc3)

        assert path is not None
        assert path.path == [doc1, doc2, doc3]
        assert path.hops == 2

    def should_return_zero_hop_path_for_same_document(self, link_index):
        doc1 = "doc1.md"

        path = link_index.find_path(doc1, doc1)

        assert path is not None
        assert path.path == [doc1]
        assert path.hops == 0