from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)          # "finnhub" | "newsapi"
    url = Column(String(1000), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    category = Column(String(50))                          # raw source category (business/technology/science/general...)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class ArticleScore(Base):
    __tablename__ = "article_scores"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    sector = Column(String(50), nullable=False, index=True)
    sentiment = Column(Float, nullable=False)     # -1..1
    impact = Column(Float, nullable=False)        # 0..10
    confidence = Column(Float, nullable=False)    # 0..1
    time_horizon = Column(String(20))             # immediate | short_term | long_term
    rationale = Column(Text)
    scored_at = Column(DateTime, default=datetime.utcnow)


class DailySectorScore(Base):
    __tablename__ = "daily_sector_scores"
    __table_args__ = (UniqueConstraint("date", "sector", name="uq_daily_sector"),)

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True)   # YYYY-MM-DD
    sector = Column(String(50), nullable=False)
    composite_score = Column(Float, nullable=False)          # -100..100
    article_count = Column(Integer, default=0)
    top_article_ids = Column(JSON)


class DailyMarketScore(Base):
    __tablename__ = "daily_market_scores"
    __table_args__ = (UniqueConstraint("date", name="uq_daily_market"),)

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True, unique=True)
    overall_score = Column(Float, nullable=False)
    narrative_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="running")   # running | success | error
    articles_fetched = Column(Integer, default=0)
    articles_scored = Column(Integer, default=0)
    error = Column(Text)
