import os
import logging
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Curated list of macro series that meaningfully move equity markets.
SERIES = {
    "CPIAUCSL": "CPI (headline inflation)",
    "CPILFESL": "Core CPI (ex food & energy)",
    "UNRATE": "Unemployment Rate",
    "PAYEMS": "Nonfarm Payrolls",
    "FEDFUNDS": "Effective Federal Funds Rate",
    "GDP": "Gross Domestic Product",
    "PCEPI": "PCE Price Index (Fed's preferred inflation gauge)",
    "RSAFS": "Retail Sales",
    "INDPRO": "Industrial Production Index",
    "UMCSENT": "Univ. of Michigan Consumer Sentiment",
}


def _api_key() -> str:
    key = os.getenv("FRBSL_API_KEY")
    if not key:
        raise RuntimeError("FRBSL_API_KEY not set")
    return key


def fetch_news() -> list[dict]:
    """Check each tracked FRED series for a new data release and synthesize it as a news-like item.

    Returns normalized dicts matching the other source clients — one per series that has a new
    observation since it was last seen, with the prior value included so the scoring model can
    judge direction and magnitude, not just the raw number. New-release detection relies on the
    pipeline's existing dedupe-by-url: the URL embeds the release date, so re-running the pipeline
    before a series publishes again is a no-op.
    """
    key = _api_key()
    articles = []
    for series_id, label in SERIES.items():
        try:
            resp = requests.get(
                BASE_URL,
                params={
                    "series_id": series_id,
                    "api_key": key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 2,
                },
                timeout=15,
            )
            resp.raise_for_status()
            obs = [o for o in resp.json().get("observations", []) if o.get("value") not in (None, ".")]
            if not obs:
                continue

            latest = obs[0]
            prior = obs[1] if len(obs) > 1 else None
            release_date = latest["date"]

            change_text = ""
            if prior:
                try:
                    delta = float(latest["value"]) - float(prior["value"])
                    change_text = f" Previous reading: {prior['value']} on {prior['date']} (change: {delta:+.2f})."
                except ValueError:
                    pass

            articles.append({
                "source": "fred",
                "url": f"https://fred.stlouisfed.org/series/{series_id}#{release_date}",
                "title": f"{label}: {latest['value']} (released {release_date})",
                "summary": f"Federal Reserve Economic Data (FRED) release for {label}.{change_text}",
                "category": "economic",
                # Use discovery time, not the economic reference-period date (e.g. "CPI for June"
                # published in July) — this is what keeps the item in *today's* News Feed and
                # aggregation, consistent with how every other source's published_at is treated.
                "published_at": datetime.now(timezone.utc),
            })
        except requests.RequestException as e:
            logger.error(f"FRED fetch failed for series={series_id}: {e}")
    return articles
