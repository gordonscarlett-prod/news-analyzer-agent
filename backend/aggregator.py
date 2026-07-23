import math
from collections import defaultdict

from sectors import SECTORS, SECTOR_WEIGHT

# Saturation constant for the tanh scaling — keeps composite scores in a
# sane -100..100 range regardless of how many articles hit a sector in a day.
SATURATION_K = 15.0


def compute_sector_scores(scores_by_sector: dict[str, list[dict]], articles_by_id: dict[int, dict]) -> dict[str, dict]:
    """Given article-level scores grouped by sector, compute each sector's daily composite.

    scores_by_sector: {sector: [ {article_id, sentiment, impact, confidence, ...}, ... ]}
    Returns {sector: {composite_score, article_count, top_article_ids, top_articles}}
    """
    result = {}
    for sector in SECTORS:
        entries = scores_by_sector.get(sector, [])
        if not entries:
            result[sector] = {
                "composite_score": 0.0,
                "article_count": 0,
                "top_article_ids": [],
                "top_articles": [],
            }
            continue

        raw = sum(e["sentiment"] * e["impact"] * e["confidence"] for e in entries)
        composite = 100.0 * math.tanh(raw / SATURATION_K)

        ranked = sorted(entries, key=lambda e: abs(e["sentiment"] * e["impact"] * e["confidence"]), reverse=True)
        top = ranked[:5]
        top_ids = [e["article_id"] for e in top]
        top_articles = [
            {"id": e["article_id"], "title": articles_by_id.get(e["article_id"], {}).get("title", ""), "rationale": e.get("rationale", "")}
            for e in top
        ]

        result[sector] = {
            "composite_score": round(composite, 2),
            "article_count": len(entries),
            "top_article_ids": top_ids,
            "top_articles": top_articles,
        }
    return result


def compute_overall_score(sector_results: dict[str, dict]) -> float:
    """Market-cap-weighted average of sector composite scores."""
    total_weight = sum(SECTOR_WEIGHT.values())
    weighted = sum(
        sector_results.get(sector, {}).get("composite_score", 0.0) * SECTOR_WEIGHT.get(sector, 0.0)
        for sector in SECTORS
    )
    return round(weighted / total_weight, 2) if total_weight else 0.0


def group_scores_by_sector(article_scores: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for s in article_scores:
        grouped[s["sector"]].append(s)
    return dict(grouped)
