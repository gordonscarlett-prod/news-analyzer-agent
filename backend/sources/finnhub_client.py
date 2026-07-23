import os
import logging
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://finnhub.io/api/v1"
_NEWS_CATEGORIES = ["general", "merger"]


def _api_key() -> str:
    key = os.getenv("FINNHUB_API_KEY")
    if not key:
        raise RuntimeError("FINNHUB_API_KEY not set")
    return key


def fetch_news() -> list[dict]:
    """Fetch market/business news from Finnhub across general + merger categories.

    Returns normalized dicts: source, url, title, summary, category, published_at.
    """
    articles = []
    for category in _NEWS_CATEGORIES:
        try:
            resp = requests.get(
                f"{BASE_URL}/news",
                params={"category": category, "token": _api_key()},
                timeout=15,
            )
            resp.raise_for_status()
            for item in resp.json():
                if not item.get("url") or not item.get("headline"):
                    continue
                published_at = None
                if item.get("datetime"):
                    published_at = datetime.fromtimestamp(item["datetime"], tz=timezone.utc)
                articles.append({
                    "source": "finnhub",
                    "url": item["url"],
                    "title": item["headline"],
                    "summary": item.get("summary") or "",
                    "category": category,
                    "published_at": published_at,
                })
        except requests.RequestException as e:
            logger.error(f"Finnhub news fetch failed for category={category}: {e}")
    return articles


def fetch_sector_quotes(sector_etf: dict[str, str]) -> dict[str, dict]:
    """Fetch current quote data for each sector's ETF. Returns {sector: {c, d, dp, ...}}."""
    quotes = {}
    for sector, ticker in sector_etf.items():
        try:
            resp = requests.get(
                f"{BASE_URL}/quote",
                params={"symbol": ticker, "token": _api_key()},
                timeout=15,
            )
            resp.raise_for_status()
            quotes[sector] = resp.json()
        except requests.RequestException as e:
            logger.error(f"Finnhub quote fetch failed for {ticker}: {e}")
    return quotes
