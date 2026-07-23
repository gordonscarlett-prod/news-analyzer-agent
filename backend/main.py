from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
import logging

from database import init_db, get_db
from models import Article, ArticleScore, DailySectorScore, DailyMarketScore, RunLog
from sectors import SECTORS
from scheduler import start_scheduler, stop_scheduler
from pipeline import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DENVER = ZoneInfo("America/Denver")


def _today() -> str:
    return datetime.now(DENVER).strftime("%Y-%m-%d")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="News Analyzer Agent — Equity Sector Impact Scoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/daily-score")
def get_daily_score(date: Optional[str] = None, db: Session = Depends(get_db)):
    date_str = date or _today()

    sector_rows = db.query(DailySectorScore).filter(DailySectorScore.date == date_str).all()
    market_row = db.query(DailyMarketScore).filter(DailyMarketScore.date == date_str).first()

    sectors = []
    for sector in SECTORS:
        row = next((r for r in sector_rows if r.sector == sector), None)
        if not row:
            sectors.append({"sector": sector, "composite_score": 0.0, "article_count": 0, "top_articles": []})
            continue
        top_ids = row.top_article_ids or []
        top_articles = []
        if top_ids:
            found = db.query(Article).filter(Article.id.in_(top_ids)).all()
            by_id = {a.id: a for a in found}
            top_articles = [
                {"id": aid, "title": by_id[aid].title, "url": by_id[aid].url}
                for aid in top_ids if aid in by_id
            ]
        sectors.append({
            "sector": sector,
            "composite_score": row.composite_score,
            "article_count": row.article_count,
            "top_articles": top_articles,
        })

    return {
        "date": date_str,
        "overall_score": market_row.overall_score if market_row else 0.0,
        "narrative": market_row.narrative_text if market_row else "",
        "sectors": sectors,
    }


@app.get("/api/sectors/{sector}/trend")
def get_sector_trend(sector: str, days: int = 30, db: Session = Depends(get_db)):
    rows = (
        db.query(DailySectorScore)
        .filter(DailySectorScore.sector == sector)
        .order_by(desc(DailySectorScore.date))
        .limit(days)
        .all()
    )
    rows.reverse()
    return {
        "sector": sector,
        "points": [{"date": r.date, "composite_score": r.composite_score, "article_count": r.article_count} for r in rows],
    }


@app.get("/api/articles")
def get_articles(
    date: Optional[str] = None,
    sector: Optional[str] = None,
    min_impact: float = 0,
    db: Session = Depends(get_db),
):
    date_str = date or _today()
    query = db.query(Article, ArticleScore).join(ArticleScore, ArticleScore.article_id == Article.id)
    query = query.filter(ArticleScore.impact >= min_impact)
    if sector:
        query = query.filter(ArticleScore.sector == sector)

    results = []
    for article, score in query.order_by(desc(ArticleScore.impact)).limit(200).all():
        published = article.published_at.strftime("%Y-%m-%d") if article.published_at else article.fetched_at.strftime("%Y-%m-%d")
        if published != date_str:
            continue
        results.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "sector": score.sector,
            "sentiment": score.sentiment,
            "impact": score.impact,
            "confidence": score.confidence,
            "time_horizon": score.time_horizon,
            "rationale": score.rationale,
        })
    return {"date": date_str, "articles": results}


@app.post("/api/run-now")
def run_now(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline)
    return {"status": "started"}


@app.get("/api/status")
def get_status(db: Session = Depends(get_db)):
    logs = db.query(RunLog).order_by(desc(RunLog.run_at)).limit(10).all()
    return {
        "runs": [
            {
                "id": r.id,
                "run_at": r.run_at.isoformat(),
                "status": r.status,
                "articles_fetched": r.articles_fetched,
                "articles_scored": r.articles_scored,
                "error": r.error,
            }
            for r in logs
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=False)
