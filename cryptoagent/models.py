from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class UserRequest:
    raw_query: str
    assets: List[str]
    window_hours: int
    report_type: str = "brief"


@dataclass
class PriceSnapshot:
    asset: str
    timestamp: datetime
    price: float
    change_24h_pct: float
    volume_24h: float


@dataclass
class NewsItem:
    asset: str
    source: str
    title: str
    url: str
    published_at: datetime
    engagement_score: float
    credibility: float
    impact_hint: float


@dataclass
class FlowMetric:
    asset: str
    metric: str
    value: float
    timestamp: datetime


@dataclass
class OnChainMetric:
    asset: str
    metric: str
    value: float
    timestamp: datetime


@dataclass
class RankedInsight:
    asset: str
    title: str
    score: float
    grade: str
    evidence: Dict[str, float] = field(default_factory=dict)


@dataclass
class FinalReport:
    request: UserRequest
    generated_at: datetime
    executive_summary: List[str]
    ranked_insights: List[RankedInsight]
    bull_case: List[str]
    bear_case: List[str]
    action_points: List[str]
