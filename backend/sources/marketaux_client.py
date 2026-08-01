import os
import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.marketaux.com/v1/news/all"


def _api_key() -> str:
    key = os.getenv("MARKETAUX_API_KEY")
    if not key:
        raise RuntimeError("MARKETAUX_API_KEY not set")
    return key


def fetch_news() -> list[dict]:
    """Fetch general US business/financial news from Marketaux.

    Marketaux tags each article with the entities (tickers) it mentions and a per-entity
    sentiment score; that's folded into the summary as extra context for the scoring model,
    but sector/impact scoring is still done by Claude like every other source.
    """
    articles = []
    try:
        resp = requests.get(
            BASE_URL,
            params={
                "language": "en",
                "countries": "us",
                "filter_entities": "true",
                "limit": 50,
                "api_token": _api_key(),
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            if not item.get("url") or not item.get("title"):
                continue

            published_at = None
            if item.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                except ValueError:
                    published_at = None

            summary = item.get("description") or item.get("snippet") or ""
            entities = item.get("entities") or []
            if entities:
                tags = ", ".join(
                    f"{e.get('symbol') or e.get('name', '?')} (sentiment {e.get('sentiment_score', 0):+.2f})"
                    for e in entities[:5]
                )
                summary = f"{summary}\nEntities mentioned: {tags}".strip()

            articles.append({
                "source": "marketaux",
                "url": item["url"],
                "title": item["title"],
                "summary": summary,
                "category": "business",
                "published_at": published_at,
            })
    except requests.RequestException as e:
        logger.error(f"Marketaux news fetch failed: {e}")
    return articles
