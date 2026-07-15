"""Tests for the recommender model: ranking, fuzzy matching, errors."""

from __future__ import annotations

import pytest

from movie_rec.recommender.model import MovieNotFoundError


def test_recommend_returns_k(recommender):
    recs = recommender.recommend("Star Voyager", k=3)
    assert len(recs) == 3
    assert all(0.0 <= r.score <= 1.0 for r in recs)
    # the query itself is never recommended
    assert all(r.title != "Star Voyager" for r in recs)


def test_recommend_surfaces_same_cluster(recommender):
    """A space movie should rank other space movies above romance movies."""
    recs = recommender.recommend("Star Voyager", k=2)
    titles = {r.title for r in recs}
    space = {"Galaxy Warriors", "Cosmic Frontier"}
    assert titles & space  # at least one space movie in the top 2
    assert recs[0].title in space


def test_fuzzy_title_resolves(recommender):
    # misspelled / partial query still resolves
    recs = recommender.recommend("star voyagr", k=2)
    assert len(recs) == 2


def test_unknown_title_raises_with_suggestions(recommender):
    with pytest.raises(MovieNotFoundError) as exc:
        recommender.recommend("zzzzzzzzzzzz nonexistent", k=5)
    assert exc.value.suggestions  # non-empty list of closest titles


def test_search_returns_titles(recommender):
    results = recommender.search("galax")
    assert "Galaxy Warriors" in results


def test_blend_alpha_changes_ranking(recommender):
    """Pure-popularity blend differs from pure-content blend."""
    recommender.blend_alpha = 1.0
    content_only = [r.title for r in recommender.recommend("Star Voyager", k=5)]
    recommender.blend_alpha = 0.0
    popularity_only = [r.title for r in recommender.recommend("Star Voyager", k=5)]
    assert content_only != popularity_only
    recommender.blend_alpha = 0.7  # restore
