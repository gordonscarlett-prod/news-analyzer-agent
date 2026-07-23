import os
import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://newsapi.org/v2/top-headlines"
_CATEGORIES = ["business", "technology", "science"]


def _api_key() -> str:
    key = os.getenv("NEWSAPI_KEY")
    if not key:
        raise RuntimeError("NEWSAPI_KEY not set")
    return key


def fetch_news() -> list[dict]:
    """Fetch US business/technology/science headlines from NewsAPI.org.

    Returns normalized dicts: source, url, title, summary, category, published_at.
    """
    articles = []
    for category in _CATEGORIES:
        try:
            resp = requests.get(
                BASE_URL,
                params={
                    "category": category,
                    "country": "us",
                    "pageSize": 50,
                    "apiKey": _api_key(),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("articles", []):
                if not item.get("url") or not item.get("title"):
                    continue
                published_at = None
                if item.get("publishedAt"):
                    try:
                        published_at = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
                    except ValueError:
                        published_at = None
                articles.append({
                    "source": "newsapi",
                    "url": item["url"],
                    "title": item["title"],
                    "summary": item.get("description") or "",
                    "category": category,
                    "published_at": published_at,
                })
        except requests.RequestException as e:
            logger.error(f"NewsAPI fetch failed for category={category}: {e}")
    return articles
