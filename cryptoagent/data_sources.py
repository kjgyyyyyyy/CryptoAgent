from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from .models import FlowMetric, NewsItem, OnChainMetric, PriceSnapshot


class DemoDataSource:
    """Deterministic local datasource for MVP development."""

    def collect_prices(self, assets: List[str]) -> List[PriceSnapshot]:
        now = datetime.now(timezone.utc)
        template: Dict[str, Dict[str, float]] = {
            "ETH": {"price": 3520.0, "change": 2.8, "volume": 18_300_000_000},
            "BMNR": {"price": 19.4, "change": -1.2, "volume": 93_000_000},
        }
        snapshots: List[PriceSnapshot] = []
        for asset in assets:
            base = template.get(asset, {"price": 1.0, "change": 0.0, "volume": 0.0})
            snapshots.append(
                PriceSnapshot(
                    asset=asset,
                    timestamp=now,
                    price=base["price"],
                    change_24h_pct=base["change"],
                    volume_24h=base["volume"],
                )
            )
        return snapshots

    def collect_news(self, assets: List[str], window_hours: int) -> List[NewsItem]:
        now = datetime.now(timezone.utc)
        items = [
            NewsItem(
                asset="ETH",
                source="ResearchDesk",
                title="ETH ETF 순유입이 3일 연속 이어지며 가격 탄력성 확대",
                url="https://example.com/eth-etf-flow",
                published_at=now - timedelta(hours=3),
                engagement_score=88,
                credibility=4.3,
                impact_hint=4.2,
            ),
            NewsItem(
                asset="ETH",
                source="ChainPulse",
                title="거래소 ETH 순유출 증가, 스테이킹 비율 동반 상승",
                url="https://example.com/eth-onchain",
                published_at=now - timedelta(hours=8),
                engagement_score=72,
                credibility=4.0,
                impact_hint=3.6,
            ),
            NewsItem(
                asset="BMNR",
                source="MarketWire",
                title="BMNR 관련 신규 채굴 인프라 투자 기사 확산",
                url="https://example.com/bmnr-mining",
                published_at=now - timedelta(hours=5),
                engagement_score=65,
                credibility=3.7,
                impact_hint=3.8,
            ),
        ]
        cutoff = now - timedelta(hours=window_hours)
        return [x for x in items if x.asset in assets and x.published_at >= cutoff]

    def collect_flows(self, assets: List[str]) -> List[FlowMetric]:
        now = datetime.now(timezone.utc)
        all_metrics = [
            FlowMetric(asset="ETH", metric="etf_netflow_usd", value=210_000_000, timestamp=now),
            FlowMetric(asset="ETH", metric="exchange_netflow_eth", value=-42_000, timestamp=now),
            FlowMetric(asset="BMNR", metric="institutional_interest_index", value=61.2, timestamp=now),
        ]
        return [m for m in all_metrics if m.asset in assets]

    def collect_onchain(self, assets: List[str]) -> List[OnChainMetric]:
        now = datetime.now(timezone.utc)
        all_metrics = [
            OnChainMetric(asset="ETH", metric="active_addresses_24h", value=541_000, timestamp=now),
            OnChainMetric(asset="ETH", metric="staking_net_change_eth", value=35_500, timestamp=now),
            OnChainMetric(asset="BMNR", metric="linked_wallet_activity_index", value=48.5, timestamp=now),
        ]
        return [m for m in all_metrics if m.asset in assets]
