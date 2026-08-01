import os
import json
import logging

import anthropic
from dotenv import load_dotenv

from sectors import SECTORS

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-5"
BATCH_SIZE = 10

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""You are a financial markets analyst. Given a batch of news articles (financial, \
economic, business, technology, or scientific), assess how each one is likely to move US equity markets \
by GICS sector over the next few trading days.

Valid sectors: {", ".join(SECTORS)}

For each article, decide which sector(s) it materially affects (usually 0-2, rarely more). If an article \
has no plausible equity-market relevance (e.g. pure human interest, sports, entertainment gossip), return \
an empty sectors list for it.

Some items are macro economic data releases (e.g. CPI, unemployment, Fed funds rate) rather than headlines — \
these include the prior reading for comparison. Judge them by the surprise/direction of the change relative \
to the prior value, and treat broad macro releases (inflation, employment, rate decisions) as affecting the \
whole market rather than a single sector — apply them across the relevant sectors (e.g. Financials for rate \
moves, or multiple/all sectors for a broad inflation or employment surprise) rather than skipping them for \
lack of a single obvious sector.

For each sector you assign to an article, provide:
- sentiment: float from -1 (very bearish for that sector) to 1 (very bullish)
- impact: float from 0 (negligible) to 10 (major market-moving event, e.g. Fed policy shift, major regulatory \
action, landmark scientific breakthrough with commercial implications)
- confidence: float from 0 to 1, how confident you are in this assessment
- time_horizon: one of "immediate" (priced in same/next day), "short_term" (days to weeks), "long_term" (months+)
- rationale: one concise sentence explaining the mechanism (why this sector, why this direction)

Be discriminating: most routine news should score low impact (0-3). Reserve impact 7+ for genuinely \
significant events (major rate decisions, large M&A, landmark regulation, breakthrough discoveries with \
clear commercial paths, geopolitical shocks)."""

SCORE_TOOL = {
    "name": "submit_scores",
    "description": "Submit sector impact scores for a batch of articles.",
    "input_schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "article_index": {"type": "integer"},
                        "sectors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sector": {"type": "string", "enum": SECTORS},
                                    "sentiment": {"type": "number"},
                                    "impact": {"type": "number"},
                                    "confidence": {"type": "number"},
                                    "time_horizon": {
                                        "type": "string",
                                        "enum": ["immediate", "short_term", "long_term"],
                                    },
                                    "rationale": {"type": "string"},
                                },
                                "required": ["sector", "sentiment", "impact", "confidence", "time_horizon", "rationale"],
                            },
                        },
                    },
                    "required": ["article_index", "sectors"],
                },
            },
        },
        "required": ["results"],
    },
}


def _score_batch(batch: list[dict]) -> dict[int, list[dict]]:
    """Score a single batch (<=BATCH_SIZE) of articles. Returns {index_in_batch: [scores]}."""
    numbered = "\n\n".join(
        f"[{i}] TITLE: {a['title']}\nSUMMARY: {a.get('summary') or '(no summary)'}"
        for i, a in enumerate(batch)
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[SCORE_TOOL],
            tool_choice={"type": "tool", "name": "submit_scores"},
            messages=[{"role": "user", "content": f"Score these articles:\n\n{numbered}"}],
        )
        for block in response.content:
            if block.type == "tool_use" and block.name == "submit_scores":
                results = block.input.get("results", [])
                scored = {}
                for r in results:
                    idx = r.get("article_index")
                    if idx is None:
                        logger.warning(f"Skipping a scored result with no article_index: {r}")
                        continue
                    scored[idx] = r.get("sectors", [])
                return scored
    except Exception as e:
        logger.error(f"Claude scoring batch failed: {e}")
    return {}


def score_articles(articles: list[dict]) -> list[dict]:
    """Score a list of normalized article dicts (with 'id', 'title', 'summary').

    Returns a flat list of score dicts: {article_id, sector, sentiment, impact, confidence, time_horizon, rationale}.
    """
    all_scores = []
    for start in range(0, len(articles), BATCH_SIZE):
        batch = articles[start:start + BATCH_SIZE]
        batch_results = _score_batch(batch)
        for idx, sector_scores in batch_results.items():
            if idx >= len(batch):
                continue
            article = batch[idx]
            for s in sector_scores:
                all_scores.append({
                    "article_id": article["id"],
                    "sector": s["sector"],
                    "sentiment": max(-1.0, min(1.0, float(s["sentiment"]))),
                    "impact": max(0.0, min(10.0, float(s["impact"]))),
                    "confidence": max(0.0, min(1.0, float(s["confidence"]))),
                    "time_horizon": s.get("time_horizon", "short_term"),
                    "rationale": s.get("rationale", ""),
                })
    return all_scores


def write_daily_narrative(sector_scores: dict[str, float], top_movers: list[dict]) -> str:
    """Ask Claude to write a short daily narrative summarizing the biggest sector movers and why."""
    movers_text = "\n".join(
        f"- {m['sector']}: {m['composite_score']:+.1f} — driven by: "
        + "; ".join(a["title"] for a in m.get("top_articles", [])[:3])
        for m in top_movers
    )
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system="You are a financial markets analyst writing a concise daily briefing.",
            messages=[{
                "role": "user",
                "content": (
                    "Write a 3-5 sentence daily market briefing summarizing today's biggest sector-level "
                    "news impact scores and what's driving them. Be specific and direct, no filler.\n\n"
                    f"Sector scores: {json.dumps(sector_scores)}\n\nTop movers:\n{movers_text}"
                ),
            }],
        )
        return "".join(b.text for b in response.content if b.type == "text").strip()
    except Exception as e:
        logger.error(f"Narrative generation failed: {e}")
        return ""
