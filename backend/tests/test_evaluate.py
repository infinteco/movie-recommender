"""Tests for the proxy-relevance evaluation harness."""

from __future__ import annotations

from movie_rec.evaluation.evaluate import evaluate


def test_evaluate_metrics_in_range(recommender):
    metrics = evaluate(recommender, k=2, min_overlap=2, sample=None)
    for key in ("precision_at_k", "recall_at_k", "coverage"):
        assert 0.0 <= metrics[key] <= 1.0
    assert metrics["n_queries_scored"] > 0


def test_evaluate_precision_positive_on_clustered_data(recommender):
    """With two clear genre clusters, precision should be well above zero."""
    metrics = evaluate(recommender, k=2, min_overlap=2, sample=None)
    assert metrics["precision_at_k"] > 0.4
