"""Specs for pure diagnostic reasoning functions."""

from zk_chat.diagnostics import Recommendation, generate_recommendations


class DescribeGenerateRecommendations:
    def should_recommend_full_reindex_when_both_collections_empty(self):
        result = generate_recommendations(0, 0, None, [], [])

        assert len(result) == 1
        assert result[0].severity == "error"
        assert "Both collections are empty" in result[0].message

    def should_recommend_reindex_when_only_documents_empty(self):
        result = generate_recommendations(0, 10, None, [], [])

        assert len(result) == 1
        assert result[0].severity == "warning"
        assert "Documents collection is empty" in result[0].message

    def should_recommend_reindex_when_only_excerpts_empty(self):
        result = generate_recommendations(10, 0, None, [], [])

        assert len(result) == 1
        assert result[0].severity == "warning"
        assert "Excerpts collection is empty" in result[0].message

    def should_report_collections_have_data_when_both_populated(self):
        result = generate_recommendations(10, 50, None, [], [])

        assert len(result) == 1
        assert result[0].severity == "ok"
        assert "Collections have data" in result[0].message

    def should_warn_about_distance_threshold_when_query_returns_no_results(self):
        result = generate_recommendations(10, 50, "test query", [], [])

        assert len(result) == 2
        assert result[1].severity == "warning"
        assert "distance threshold" in result[1].message

    def should_include_detail_in_distance_threshold_warning(self):
        result = generate_recommendations(10, 50, "test query", [], [])

        assert result[1].detail is not None
        assert "different query" in result[1].detail

    def should_not_warn_about_query_when_no_query_provided(self):
        result = generate_recommendations(10, 50, None, [], [])

        assert len(result) == 1

    def should_not_warn_about_query_when_results_exist(self):
        result = generate_recommendations(10, 50, "test query", ["result1"], ["excerpt1"])

        assert len(result) == 1

    def should_return_recommendation_models(self):
        result = generate_recommendations(0, 0, None, [], [])

        assert all(isinstance(r, Recommendation) for r in result)
