import logging
from datetime import datetime, timezone

from database import SessionLocal
from models import Article, ArticleScore, DailySectorScore, DailyMarketScore, RunLog
from sources import finnhub_client, newsapi_client, marketaux_client, fred_client
from scoring import score_articles, write_daily_narrative
from aggregator import compute_sector_scores, compute_overall_score, group_scores_by_sector

logger = logging.getLogger(__name__)


def _fetch_and_store_articles(db) -> list[Article]:
    """Fetch from all sources, insert new articles (deduped by url), return newly inserted rows."""
    raw = []
    try:
        raw.extend(finnhub_client.fetch_news())
    except Exception as e:
        logger.error(f"Finnhub fetch error: {e}")
    try:
        raw.extend(newsapi_client.fetch_news())
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")
    try:
        raw.extend(marketaux_client.fetch_news())
    except Exception as e:
        logger.error(f"Marketaux fetch error: {e}")
    try:
        raw.extend(fred_client.fetch_news())
    except Exception as e:
        logger.error(f"FRED fetch error: {e}")

    new_articles = []
    for item in raw:
        exists = db.query(Article).filter(Article.url == item["url"]).first()
        if exists:
            continue
        article = Article(
            source=item["source"],
            url=item["url"],
            title=item["title"],
            summary=item.get("summary", ""),
            category=item.get("category"),
            published_at=item.get("published_at"),
        )
        db.add(article)
        new_articles.append(article)

    db.commit()
    for a in new_articles:
        db.refresh(a)
    return new_articles


def run_pipeline(target_date: str | None = None) -> dict:
    """Fetch, score, and aggregate today's news. Returns a summary dict."""
    db = SessionLocal()
    run_log = RunLog(status="running")
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    try:
        date_str = target_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        new_articles = _fetch_and_store_articles(db)
        run_log.articles_fetched = len(new_articles)

        if not new_articles:
            logger.info("No new articles fetched; skipping scoring.")
            scored_count = 0
        else:
            article_dicts = [{"id": a.id, "title": a.title, "summary": a.summary} for a in new_articles]
            article_scores = score_articles(article_dicts)
            scored_count = len(article_scores)

            for s in article_scores:
                db.add(ArticleScore(
                    article_id=s["article_id"],
                    sector=s["sector"],
                    sentiment=s["sentiment"],
                    impact=s["impact"],
                    confidence=s["confidence"],
                    time_horizon=s["time_horizon"],
                    rationale=s["rationale"],
                ))
            db.commit()

            articles_by_id = {a["id"]: a for a in article_dicts}
            grouped = group_scores_by_sector(article_scores)
            sector_results = compute_sector_scores(grouped, articles_by_id)
            overall_score = compute_overall_score(sector_results)

            for sector, result in sector_results.items():
                existing = db.query(DailySectorScore).filter_by(date=date_str, sector=sector).first()
                if existing:
                    existing.composite_score = result["composite_score"]
                    existing.article_count = result["article_count"]
                    existing.top_article_ids = result["top_article_ids"]
                else:
                    db.add(DailySectorScore(
                        date=date_str,
                        sector=sector,
                        composite_score=result["composite_score"],
                        article_count=result["article_count"],
                        top_article_ids=result["top_article_ids"],
                    ))

            top_movers = sorted(
                [{"sector": s, **r} for s, r in sector_results.items()],
                key=lambda r: abs(r["composite_score"]),
                reverse=True,
            )[:5]
            narrative = write_daily_narrative(
                {s: r["composite_score"] for s, r in sector_results.items()}, top_movers
            )

            existing_market = db.query(DailyMarketScore).filter_by(date=date_str).first()
            if existing_market:
                existing_market.overall_score = overall_score
                existing_market.narrative_text = narrative
            else:
                db.add(DailyMarketScore(date=date_str, overall_score=overall_score, narrative_text=narrative))

            db.commit()

        run_log.status = "success"
        run_log.articles_scored = scored_count
        db.commit()
        return {"status": "success", "articles_fetched": run_log.articles_fetched, "articles_scored": scored_count}

    except Exception as e:
        logger.exception(f"Pipeline run failed: {e}")
        db.rollback()
        run_log.status = "error"
        run_log.error = str(e)
        db.commit()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
