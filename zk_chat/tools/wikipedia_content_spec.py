import pytest
from unittest.mock import patch, MagicMock
from wikipedia.exceptions import DisambiguationError
from .wikipedia_content import LookUpTopicOnWikipedia, WikipediaContentResult


class DescribeWikipediaContentTool:
    @pytest.fixture
    def tool(self):
        return LookUpTopicOnWikipedia()

    def should_retrieve_article_content_successfully(self, tool):
        with patch('wikipedia.search') as mock_search, \
             patch('wikipedia.page') as mock_page:
            # Mock search results
            mock_search.return_value = ['Python (programming language)']

            # Mock page content
            mock_page_instance = MagicMock()
            mock_page_instance.title = 'Python (programming language)'
            mock_page_instance.summary = 'Python is a high-level programming language.'
            mock_page_instance.url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
            mock_page.return_value = mock_page_instance

            result = tool.run('Python programming')

            assert isinstance(result, dict)
            assert result['title'] == 'Python (programming language)'
            assert result['content'] == 'Python is a high-level programming language.'
            assert result['url'] == 'https://en.wikipedia.org/wiki/Python_(programming_language)'

    def should_handle_no_search_results(self, tool):
        with patch('wikipedia.search') as mock_search:
            mock_search.return_value = []

            result = tool.run('nonexistent topic 123456789')

            assert isinstance(result, dict)
            assert result['title'] == 'No results'
            assert "No Wikipedia articles found" in result['content']
            assert result['url'] is None

    def should_handle_disambiguation_pages(self, tool):
        with patch('wikipedia.search') as mock_search, \
             patch('wikipedia.page') as mock_page:

            # First call raises DisambiguationError
            mock_search.return_value = ['Python']
            mock_page.side_effect = [
                DisambiguationError('Python', ['Python (programming language)', 'Python (snake)']),
                MagicMock(
                    title='Python (programming language)',
                    summary='Python is a programming language.',
                    url='https://en.wikipedia.org/wiki/Python_(programming_language)'
                )
            ]

            result = tool.run('Python')

            assert isinstance(result, dict)
            assert result['title'] == 'Python (programming language)'
            assert result['content'] == 'Python is a programming language.'
            assert result['url'] == 'https://en.wikipedia.org/wiki/Python_(programming_language)'

    def should_handle_general_errors_gracefully(self, tool):
        with patch('wikipedia.search') as mock_search:
            mock_search.side_effect = Exception('Network error')

            result = tool.run('Python')

            assert isinstance(result, dict)
            assert result['title'] == 'Error'
            assert 'Network error' in result['content']
            assert result['url'] is None
