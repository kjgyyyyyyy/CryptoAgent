from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from .models import FlowMetric, NewsItem, OnChainMetric, RankedInsight


def _grade(score: float) -> str:
    if score >= 4.2:
        return "S"
    if score >= 3.4:
        return "A"
    if score >= 2.4:
        return "B"
    return "C"


def rank_insights(news: List[NewsItem], flows: List[FlowMetric], onchain: List[OnChainMetric]) -> List[RankedInsight]:
    now = datetime.now(timezone.utc)

    flow_index: Dict[str, float] = {}
    for flow in flows:
        flow_index[flow.asset] = flow_index.get(flow.asset, 0.0) + abs(flow.value)

    onchain_index: Dict[str, float] = {}
    for metric in onchain:
        onchain_index[metric.asset] = onchain_index.get(metric.asset, 0.0) + abs(metric.value)

    ranked: List[RankedInsight] = []
    for item in news:
        age_hours = max(1.0, (now - item.published_at).total_seconds() / 3600)
        timeliness = max(1.0, 5.0 - age_hours / 6.0)
        market_reaction = min(5.0, 1.0 + (flow_index.get(item.asset, 0.0) > 0) + (onchain_index.get(item.asset, 0.0) > 0))
        impact = min(5.0, item.impact_hint)
        credibility = min(5.0, item.credibility)

        score = (
            0.35 * impact
            + 0.25 * credibility
            + 0.20 * timeliness
            + 0.20 * market_reaction
        )

        ranked.append(
            RankedInsight(
                asset=item.asset,
                title=item.title,
                score=round(score, 2),
                grade=_grade(score),
                evidence={
                    "impact": round(impact, 2),
                    "credibility": round(credibility, 2),
                    "timeliness": round(timeliness, 2),
                    "market_reaction": round(market_reaction, 2),
                },
            )
        )

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked
