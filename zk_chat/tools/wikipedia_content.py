from typing import Optional

import wikipedia
from mojentic.llm.tools.llm_tool import LLMTool
from pydantic import BaseModel


class WikipediaContentResult(BaseModel):
    title: str
    content: str
    url: Optional[str]


class LookUpTopicOnWikipedia(LLMTool):
    """Tool for retrieving content from Wikipedia for a given entity."""

    def run(self, topic: str) -> WikipediaContentResult:
        try:
            # Search for the page
            search_results = wikipedia.search(topic)
            if not search_results:
                return WikipediaContentResult(
                    title="No results",
                    content=f"No Wikipedia articles found for '{topic}'",
                    url=None
                ).model_dump()

            # Get the top result
            page_title = search_results[0]
            page = wikipedia.page(page_title, auto_suggest=False)

            return WikipediaContentResult(
                title=page.title,
                content=page.summary,
                url=page.url
            ).model_dump()

        except wikipedia.DisambiguationError as e:
            # Handle disambiguation pages by taking the first option
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                return WikipediaContentResult(
                    title=page.title,
                    content=page.summary,
                    url=page.url
                ).model_dump()
            except:
                return WikipediaContentResult(
                    title="Disambiguation Error",
                    content=f"Multiple matches found for '{topic}'. Please be more specific.",
                    url=None
                ).model_dump()
        except Exception as e:
            return WikipediaContentResult(
                title="Error",
                content=f"An error occurred while retrieving Wikipedia content: {str(e)}",
                url=None
            ).model_dump()

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "lookup_topic_on_wikipedia",
                "description": "Retrieves information about a given topic from Wikipedia.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic I'd like to learn about."
                        }
                    },
                    "required": ["topic"]
                }
            }
        }
