"""
Link Traversal Service for Zettelkasten

This service provides functionality for analyzing and traversing the wikilink graph
structure of a Zettelkasten. It handles wikilink extraction, resolution, backlink
discovery, and graph analysis operations.
"""
import re
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple, Iterator
from pathlib import Path

import structlog
from pydantic import BaseModel

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway, WikiLink

logger = structlog.get_logger()


class WikiLinkReference(BaseModel):
    """A WikiLink with additional context about its location in the document."""
    wikilink: WikiLink
    line_number: int
    context_snippet: str
    source_document: str


class BacklinkResult(BaseModel):
    """Result of a backlink search - a document that links to the target."""
    linking_document: str
    target_wikilink: str
    resolved_target: Optional[str]
    line_number: int
    context_snippet: str


class ForwardLinkResult(BaseModel):
    """Result of a forward link search - a document linked from the source."""
    source_document: str
    target_wikilink: str
    resolved_target: Optional[str]
    line_number: int
    context_snippet: str


class LinkPath(BaseModel):
    """A path through the link graph between two documents."""
    from_document: str
    to_document: str
    path: List[str]
    hops: int


class LinkMetrics(BaseModel):
    """Metrics about the link graph structure."""
    total_documents: int
    total_links: int
    total_resolved_links: int
    total_broken_links: int
    orphaned_documents: List[str]  # documents with no incoming links
    hub_documents: List[Tuple[str, int]]  # documents with most incoming links
    average_links_per_document: float
    link_density: float  # ratio of actual links to possible links


class LinkGraphIndex:
    """In-memory index of the wikilink graph structure for fast traversal."""

    def __init__(self):
        self.forward_links: Dict[str, Set[str]] = {}  # document -> documents it links to
        self.backward_links: Dict[str, Set[str]] = {}  # document -> documents that link to it
        self.broken_links: Dict[str, Set[str]] = {}  # document -> broken wikilinks
        self.wikilink_references: Dict[str, List[WikiLinkReference]] = {}  # cached extractions
        self.last_updated: Optional[datetime] = None

    def add_document_links(self, document: str, wikilink_refs: List[WikiLinkReference],
                          resolved_targets: Dict[str, Optional[str]]) -> None:
        """Add or update links for a document."""
        # Clear existing links for this document
        if document in self.forward_links:
            for target in self.forward_links[document]:
                if target in self.backward_links:
                    self.backward_links[target].discard(document)

        # Reset for this document
        self.forward_links[document] = set()
        self.broken_links[document] = set()
        self.wikilink_references[document] = wikilink_refs

        # Add new links
        for ref in wikilink_refs:
            wikilink_title = ref.wikilink.title
            resolved_target = resolved_targets.get(wikilink_title)

            if resolved_target:
                # Valid link
                self.forward_links[document].add(resolved_target)
                if resolved_target not in self.backward_links:
                    self.backward_links[resolved_target] = set()
                self.backward_links[resolved_target].add(document)
            else:
                # Broken link
                self.broken_links[document].add(wikilink_title)

    def get_forward_links(self, document: str) -> Set[str]:
        """Get documents that this document links to."""
        return self.forward_links.get(document, set())

    def get_backward_links(self, document: str) -> Set[str]:
        """Get documents that link to this document."""
        return self.backward_links.get(document, set())

    def get_broken_links(self, document: str) -> Set[str]:
        """Get broken wikilinks from this document."""
        return self.broken_links.get(document, set())

    def find_path(self, from_doc: str, to_doc: str, max_hops: int = 3) -> Optional[LinkPath]:
        """Find shortest path between documents using BFS."""
        if from_doc == to_doc:
            return LinkPath(from_document=from_doc, to_document=to_doc, path=[from_doc], hops=0)

        visited = {from_doc}
        queue = [(from_doc, [from_doc])]

        for _ in range(max_hops):
            if not queue:
                break

            current_level = []
            while queue:
                current_doc, path = queue.pop(0)

                for next_doc in self.get_forward_links(current_doc):
                    if next_doc == to_doc:
                        final_path = path + [next_doc]
                        return LinkPath(
                            from_document=from_doc,
                            to_document=to_doc,
                            path=final_path,
                            hops=len(final_path) - 1
                        )

                    if next_doc not in visited:
                        visited.add(next_doc)
                        current_level.append((next_doc, path + [next_doc]))

            queue = current_level

        return None  # No path found within max_hops


class LinkTraversalService:
    """
    Service for analyzing and traversing wikilink relationships in a Zettelkasten.

    Provides functionality for:
    - Extracting wikilinks from documents
    - Finding backlinks and forward links
    - Building and maintaining a link graph index
    - Analyzing link patterns and metrics
    - Finding paths between documents
    """

    def __init__(self, filesystem_gateway: MarkdownFilesystemGateway):
        self.filesystem_gateway = filesystem_gateway
        self.link_index = LinkGraphIndex()
        self._wikilink_pattern = re.compile(r'\[\[(.*?)(?:\|(.*?))?\]\]')

    def extract_wikilinks_from_content(self, content: str, source_document: str = "") -> List[WikiLinkReference]:
        """
        Extract all wikilinks from document content with context information.

        Args:
            content: The document content to analyze
            source_document: The source document path for reference

        Returns:
            List of WikiLinkReference objects with line numbers and context
        """
        wikilink_references = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            matches = self._wikilink_pattern.finditer(line)
            for match in matches:
                try:
                    # Parse the full wikilink
                    wikilink = WikiLink.parse(match.group(0))

                    # Create context snippet (surrounding words)
                    context_snippet = self._create_context_snippet(line, match.start(), match.end())

                    wikilink_ref = WikiLinkReference(
                        wikilink=wikilink,
                        line_number=line_num,
                        context_snippet=context_snippet,
                        source_document=source_document
                    )
                    wikilink_references.append(wikilink_ref)

                except ValueError as e:
                    logger.warning("Failed to parse wikilink",
                                   wikilink_text=match.group(0),
                                   line_number=line_num,
                                   source_document=source_document,
                                   error=str(e))
                    continue

        return wikilink_references

    def extract_wikilinks_from_document(self, relative_path: str) -> List[WikiLinkReference]:
        """
        Extract all wikilinks from a specific document.

        Args:
            relative_path: Path to the document to analyze

        Returns:
            List of WikiLinkReference objects
        """
        if not self.filesystem_gateway.path_exists(relative_path):
            logger.warning("Document not found for wikilink extraction", path=relative_path)
            return []

        try:
            metadata, content = self.filesystem_gateway.read_markdown(relative_path)
            return self.extract_wikilinks_from_content(content, relative_path)
        except Exception as e:
            logger.error("Failed to extract wikilinks from document",
                        path=relative_path, error=str(e))
            return []

    def find_backlinks(self, target_document: str) -> List[BacklinkResult]:
        """
        Find all documents that link to the target document.

        Args:
            target_document: The document to find backlinks for

        Returns:
            List of BacklinkResult objects
        """
        backlinks = []
        target_title = Path(target_document).stem

        # If we have a current index, use it
        if target_document in self.link_index.backward_links:
            linking_docs = self.link_index.backward_links[target_document]
            for linking_doc in linking_docs:
                if linking_doc in self.link_index.wikilink_references:
                    for ref in self.link_index.wikilink_references[linking_doc]:
                        if ref.wikilink.title == target_title:
                            backlinks.append(BacklinkResult(
                                linking_document=linking_doc,
                                target_wikilink=str(ref.wikilink),
                                resolved_target=target_document,
                                line_number=ref.line_number,
                                context_snippet=ref.context_snippet
                            ))
            return backlinks

        # Fall back to scanning all documents
        logger.info("Scanning all documents for backlinks", target=target_document)
        for relative_path in self.filesystem_gateway.iterate_markdown_files():
            wikilink_refs = self.extract_wikilinks_from_document(relative_path)
            for ref in wikilink_refs:
                try:
                    resolved_path = self.filesystem_gateway.resolve_wikilink(str(ref.wikilink))
                    if resolved_path == target_document:
                        backlinks.append(BacklinkResult(
                            linking_document=relative_path,
                            target_wikilink=str(ref.wikilink),
                            resolved_target=target_document,
                            line_number=ref.line_number,
                            context_snippet=ref.context_snippet
                        ))
                except ValueError:
                    # Wikilink doesn't resolve, skip
                    continue

        return backlinks

    def find_forward_links(self, source_document: str) -> List[ForwardLinkResult]:
        """
        Find all documents that are linked from the source document.

        Args:
            source_document: The document to find forward links from

        Returns:
            List of ForwardLinkResult objects
        """
        forward_links = []
        wikilink_refs = self.extract_wikilinks_from_document(source_document)

        for ref in wikilink_refs:
            try:
                resolved_path = self.filesystem_gateway.resolve_wikilink(str(ref.wikilink))
                forward_links.append(ForwardLinkResult(
                    source_document=source_document,
                    target_wikilink=str(ref.wikilink),
                    resolved_target=resolved_path,
                    line_number=ref.line_number,
                    context_snippet=ref.context_snippet
                ))
            except ValueError:
                # Broken link
                forward_links.append(ForwardLinkResult(
                    source_document=source_document,
                    target_wikilink=str(ref.wikilink),
                    resolved_target=None,
                    line_number=ref.line_number,
                    context_snippet=ref.context_snippet
                ))

        return forward_links

    def build_link_index(self) -> None:
        """Build or rebuild the complete link graph index."""
        logger.info("Building link graph index")
        self.link_index = LinkGraphIndex()

        for relative_path in self.filesystem_gateway.iterate_markdown_files():
            wikilink_refs = self.extract_wikilinks_from_document(relative_path)

            # Resolve all wikilinks for this document
            resolved_targets = {}
            for ref in wikilink_refs:
                try:
                    resolved = self.filesystem_gateway.resolve_wikilink(str(ref.wikilink))
                    resolved_targets[ref.wikilink.title] = resolved
                except ValueError:
                    resolved_targets[ref.wikilink.title] = None

            self.link_index.add_document_links(relative_path, wikilink_refs, resolved_targets)

        self.link_index.last_updated = datetime.now()
        logger.info("Link graph index built",
                   documents=len(self.link_index.forward_links),
                   total_links=sum(len(links) for links in self.link_index.forward_links.values()))

    def find_link_path(self, from_document: str, to_document: str, max_hops: int = 3) -> Optional[LinkPath]:
        """
        Find a path between two documents through wikilinks.

        Args:
            from_document: Starting document
            to_document: Target document
            max_hops: Maximum number of hops to search

        Returns:
            LinkPath object if a path exists, None otherwise
        """
        # Ensure index is built
        if not self.link_index.last_updated:
            self.build_link_index()

        return self.link_index.find_path(from_document, to_document, max_hops)

    def get_link_metrics(self, document: Optional[str] = None) -> LinkMetrics:
        """
        Get metrics about the link graph structure.

        Args:
            document: Optional specific document to analyze, or None for global metrics

        Returns:
            LinkMetrics object with graph statistics
        """
        # Ensure index is built
        if not self.link_index.last_updated:
            self.build_link_index()

        if document:
            # Metrics for specific document
            forward_links = len(self.link_index.get_forward_links(document))
            backward_links = len(self.link_index.get_backward_links(document))
            broken_links = len(self.link_index.get_broken_links(document))

            return LinkMetrics(
                total_documents=1,
                total_links=forward_links,
                total_resolved_links=forward_links,
                total_broken_links=broken_links,
                orphaned_documents=[document] if backward_links == 0 else [],
                hub_documents=[(document, backward_links)],
                average_links_per_document=float(forward_links),
                link_density=0.0  # Not meaningful for single document
            )

        # Global metrics
        total_documents = len(self.link_index.forward_links)
        total_links = sum(len(links) for links in self.link_index.forward_links.values())
        total_broken = sum(len(broken) for broken in self.link_index.broken_links.values())

        # Find orphaned documents (no incoming links)
        orphaned = []
        for doc in self.link_index.forward_links:
            if len(self.link_index.get_backward_links(doc)) == 0:
                orphaned.append(doc)

        # Find hub documents (most incoming links)
        hub_scores = [(doc, len(self.link_index.get_backward_links(doc)))
                     for doc in self.link_index.forward_links]
        hub_documents = sorted(hub_scores, key=lambda x: x[1], reverse=True)[:10]

        # Calculate metrics
        avg_links = total_links / total_documents if total_documents > 0 else 0.0
        max_possible_links = total_documents * (total_documents - 1)
        link_density = total_links / max_possible_links if max_possible_links > 0 else 0.0

        return LinkMetrics(
            total_documents=total_documents,
            total_links=total_links,
            total_resolved_links=total_links,  # Only resolved links are in the index
            total_broken_links=total_broken,
            orphaned_documents=orphaned,
            hub_documents=hub_documents,
            average_links_per_document=avg_links,
            link_density=link_density
        )

    def _create_context_snippet(self, line: str, start: int, end: int, context_chars: int = 50) -> str:
        """Create a context snippet showing the wikilink within its surrounding text."""
        # Get context before and after the wikilink
        context_start = max(0, start - context_chars)
        context_end = min(len(line), end + context_chars)

        snippet = line[context_start:context_end].strip()

        # If we truncated, add ellipses
        if context_start > 0:
            snippet = "..." + snippet
        if context_end < len(line):
            snippet = snippet + "..."

        return snippet