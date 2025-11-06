import re
from collections.abc import Iterator

from pydantic import BaseModel

from zk_chat.filesystem_gateway import FilesystemGateway
from zk_chat.markdown.markdown_utilities import MarkdownUtilities


class WikiLink(BaseModel):
    title: str
    caption: str | None

    @classmethod
    def parse(cls, value: str) -> "WikiLink":
        # parse incoming value according to [[title|caption]] where the caption is optional
        # Use a regex
        pattern = r'\[\[(.*?)(?:\|(.*?))?\]\]'
        match = re.match(pattern, value)

        if not match:
            raise ValueError(f"Invalid wikilink format: {value}")

        title = match.group(1).strip()
        caption = match.group(2).strip() if match.group(2) else None

        return WikiLink(title=title, caption=caption)

    def __str__(self):
        result = self.title
        if self.caption:
            result += f'|{self.caption}'
        return f"[[{result}]]"


class MarkdownFilesystemGateway(FilesystemGateway):
    """Gateway for markdown filesystem operations that abstracts OS dependencies and markdown
    handling."""

    def resolve_wikilink(self, wikilink: str) -> str:
        link = WikiLink.parse(wikilink)
        for root, _, files in self._walk_filesystem():
            for file in files:
                if file == link.title or file == link.title + ".md":
                    full_path = self.join_paths(root, file)
                    return self._get_relative_path(full_path)
        raise ValueError(f"Could not resolve wikilink: {wikilink}")

    def iterate_markdown_files(self) -> Iterator[str]:
        """Iterate through all markdown files in the root directory.

        Yields:
            str: Relative path for each markdown file
        """
        yield from self.iterate_files_by_extensions(['.md'])

    def read_markdown(self, relative_path: str) -> tuple[dict, str]:
        """Read a markdown file and split it into metadata and content.

        Args:
            relative_path: Relative path to the markdown file

        Returns:
            Tuple[Dict, str]: A tuple containing the metadata dictionary and the content string
        """
        full_path = self._get_full_path(relative_path)
        return MarkdownUtilities.load_markdown(full_path)

    def write_markdown(self, relative_path: str, metadata: dict, content: str) -> None:
        """Write metadata and content to a markdown file.

        Args:
            relative_path: Relative path to the markdown file
            metadata: Metadata to write to the file
            content: Content to write to the file
        """
        import yaml
        metadata_yaml = yaml.dump(metadata, Dumper=yaml.SafeDumper)
        file_content = f"---\n{metadata_yaml}---\n{content}"
        self.write_file(relative_path, file_content)
