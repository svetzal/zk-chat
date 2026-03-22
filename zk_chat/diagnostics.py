"""Pure diagnostic reasoning functions for index health assessment."""

from pydantic import BaseModel, ConfigDict


class Recommendation(BaseModel):
    """A single diagnostic recommendation with severity and message."""

    model_config = ConfigDict(frozen=True)

    severity: str  # "error", "warning", "ok"
    message: str
    detail: str | None = None


def generate_recommendations(
    doc_count: int,
    excerpt_count: int,
    query: str | None,
    doc_results: list,
    excerpt_results: list,
) -> list[Recommendation]:
    """Generate diagnostic recommendations based on collection state and query results.

    Parameters
    ----------
    doc_count : int
        Number of documents in the documents collection.
    excerpt_count : int
        Number of documents in the excerpts collection.
    query : str | None
        Test query that was run, or None if no query was run.
    doc_results : list
        Results from the documents query.
    excerpt_results : list
        Results from the excerpts query.

    Returns
    -------
    list[Recommendation]
        Ordered list of recommendations to display.
    """
    recommendations: list[Recommendation] = []

    if doc_count == 0 and excerpt_count == 0:
        recommendations.append(
            Recommendation(
                severity="error",
                message="Both collections are empty - run zk-chat index update --full",
            )
        )
    elif doc_count == 0:
        recommendations.append(
            Recommendation(
                severity="warning",
                message="Documents collection is empty - run zk-chat index update --full",
            )
        )
    elif excerpt_count == 0:
        recommendations.append(
            Recommendation(
                severity="warning",
                message="Excerpts collection is empty - run zk-chat index update --full",
            )
        )
    else:
        recommendations.append(Recommendation(severity="ok", message="Collections have data"))
        if query and not doc_results and not excerpt_results:
            recommendations.append(
                Recommendation(
                    severity="warning",
                    message="Query returned no results - this may be a distance threshold issue",
                    detail="Try a different query or check if your model is working correctly",
                )
            )

    return recommendations
