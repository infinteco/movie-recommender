"""Offline evaluation of the recommender.

There is **no ground-truth relevance** for a content-based recommender, so this
uses a transparent *proxy*: two movies are "relevant" to each other when their
combined genre+keyword token sets overlap by at least ``min_overlap`` tokens.
Reported metrics — Precision@k, Recall@k, catalog coverage — are therefore
proxy metrics, and the README says so explicitly. This is **not** an accuracy.
"""

from __future__ import annotations

import argparse
import random

from movie_rec.logging_config import get_logger
from movie_rec.recommender.build import build_recommender
from movie_rec.recommender.model import Recommender

logger = get_logger(__name__)


def _token_sets(recommender: Recommender) -> dict[int, set[str]]:
    """Map each movie id to its combined {genres ∪ keywords} token set."""
    sets: dict[int, set[str]] = {}
    for _, row in recommender.catalog.iterrows():
        tokens = {g.lower() for g in row["genre_list"]}
        tokens |= {k.lower() for k in row["keyword_list"]}
        sets[int(row["id"])] = tokens
    return sets


def evaluate(
    recommender: Recommender,
    k: int = 10,
    min_overlap: int = 2,
    sample: int | None = 500,
    seed: int = 42,
) -> dict[str, float]:
    """Compute Precision@k, Recall@k and catalog coverage under the proxy.

    Args:
        k: cutoff for the ranked list.
        min_overlap: shared genre+keyword tokens required to count as relevant.
        sample: number of query movies to evaluate (None = all).
        seed: RNG seed for sampling.
    """
    token_sets = _token_sets(recommender)
    ids = list(token_sets)

    query_ids = ids
    if sample is not None and sample < len(ids):
        query_ids = random.Random(seed).sample(ids, sample)

    id_to_title = dict(zip(recommender.catalog["id"], recommender.catalog["title"], strict=True))

    precisions: list[float] = []
    recalls: list[float] = []
    recommended_pool: set[int] = set()
    n_scored = 0

    for qid in query_ids:
        q_tokens = token_sets[qid]
        relevant = {
            other
            for other in ids
            if other != qid and len(q_tokens & token_sets[other]) >= min_overlap
        }
        if not relevant:
            continue  # undefined recall; skip and report how many we scored

        recs = recommender.recommend(id_to_title[qid], k=k)
        rec_ids = [r.id for r in recs]
        recommended_pool.update(rec_ids)

        hits = sum(1 for rid in rec_ids if rid in relevant)
        precisions.append(hits / k)
        recalls.append(hits / min(len(relevant), k))
        n_scored += 1

    coverage = len(recommended_pool) / len(ids) if ids else 0.0
    return {
        "precision_at_k": sum(precisions) / len(precisions) if precisions else 0.0,
        "recall_at_k": sum(recalls) / len(recalls) if recalls else 0.0,
        "coverage": coverage,
        "n_queries_scored": float(n_scored),
        "k": float(k),
        "min_overlap": float(min_overlap),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the recommender (proxy relevance).")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--min-overlap", type=int, default=2)
    parser.add_argument("--sample", type=int, default=500, help="query movies to score")
    parser.add_argument("--no-synthetic", action="store_true", help="fail if real data missing")
    args = parser.parse_args()

    recommender = build_recommender(allow_synthetic=not args.no_synthetic, persist=False)
    metrics = evaluate(
        recommender,
        k=args.k,
        min_overlap=args.min_overlap,
        sample=args.sample,
    )

    print("\n=== Recommender evaluation (PROXY relevance) ===")
    print(f"Relevance proxy: >= {args.min_overlap} shared genre+keyword tokens")
    print(f"Queries scored : {int(metrics['n_queries_scored'])} (sample={args.sample})")
    print(f"Precision@{args.k}   : {metrics['precision_at_k']:.3f}")
    print(f"Recall@{args.k}      : {metrics['recall_at_k']:.3f}")
    print(f"Catalog coverage: {metrics['coverage']:.3f}")


if __name__ == "__main__":
    main()
