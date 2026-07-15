"""Popularity signal: the IMDb weighted rating, and helpers to blend it."""

from __future__ import annotations

import numpy as np
import pandas as pd


def weighted_rating(df: pd.DataFrame, quantile: float = 0.80) -> pd.Series:
    """IMDb weighted rating (WR) per row.

        WR = (v / (v + m)) * R + (m / (v + m)) * C

    where ``R`` = ``vote_average``, ``v`` = ``vote_count``, ``C`` = mean vote
    across the catalog, and ``m`` = the ``quantile`` of ``vote_count`` (the
    minimum votes to be considered). This rewards films that are both well-rated
    and widely voted, damping tiny-sample outliers.
    """
    v = df["vote_count"].astype(float)
    r = df["vote_average"].astype(float)
    c = r.mean()
    m = v.quantile(quantile)
    return (v / (v + m)) * r + (m / (v + m)) * c


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Scale to [0, 1]; returns all-zeros if the series is constant."""
    lo, hi = float(series.min()), float(series.max())
    if hi - lo < 1e-12:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - lo) / (hi - lo)
