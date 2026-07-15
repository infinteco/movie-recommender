"""Tests for the weighted-rating popularity signal."""

from __future__ import annotations

import pandas as pd

from movie_rec.recommender.ranking import min_max_normalize, weighted_rating


def test_weighted_rating_between_rating_and_mean():
    df = pd.DataFrame({"vote_average": [9.0, 5.0], "vote_count": [10000, 10]})
    wr = weighted_rating(df, quantile=0.5)
    # High-vote film stays near its own rating; low-vote film is pulled to mean.
    assert wr.iloc[0] > wr.iloc[1]
    assert wr.iloc[0] > 7.0


def test_min_max_normalize_range():
    s = pd.Series([10.0, 20.0, 30.0])
    n = min_max_normalize(s)
    assert n.min() == 0.0
    assert n.max() == 1.0


def test_min_max_normalize_constant():
    s = pd.Series([5.0, 5.0, 5.0])
    assert (min_max_normalize(s) == 0.0).all()
