from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from .models import FinalReport, FlowMetric, OnChainMetric, PriceSnapshot, RankedInsight, UserRequest


def _price_line(price: PriceSnapshot) -> str:
    direction = "상승" if price.change_24h_pct >= 0 else "하락"
    return f"{price.asset}: ${price.price:,.2f} ({price.change_24h_pct:+.2f}%, 24h {direction})"


def build_report(
    request: UserRequest,
    prices: List[PriceSnapshot],
    ranked: List[RankedInsight],
    flows: List[FlowMetric],
    onchain: List[OnChainMetric],
) -> FinalReport:
    flow_map = {f"{x.asset}:{x.metric}": x.value for x in flows}
    onchain_map = {f"{x.asset}:{x.metric}": x.value for x in onchain}

    summary = [_price_line(p) for p in prices]
    if "ETH:etf_netflow_usd" in flow_map:
        summary.append(f"ETH ETF 순유입: ${flow_map['ETH:etf_netflow_usd']:,.0f}")
    if "ETH:exchange_netflow_eth" in flow_map:
        summary.append(f"거래소 ETH 순유입/유출: {flow_map['ETH:exchange_netflow_eth']:,.0f} ETH")

    top_titles = [f"[{x.grade}] {x.title}" for x in ranked[:3]]

    bull_case = [
        "ETF/기관 수급이 유지되면 ETH 모멘텀 지속 가능성.",
        "온체인 활동 증가와 거래소 순유출 조합은 매도 압력 완화 신호.",
    ]
    bear_case = [
        "수급 둔화 시 고점 피로도와 변동성 확대 가능성.",
        "BMNR은 뉴스 대비 실적/공시 확인 전까지 변동성 리스크 존재.",
    ]
    if "ETH:active_addresses_24h" in onchain_map:
        bull_case.append(f"ETH 활성 주소: {onchain_map['ETH:active_addresses_24h']:,.0f}")

    action_points = [
        "다음 리포트에서 ETF 순유입의 연속성 확인",
        "ETH 펀딩비/OI 과열 여부와 가격 괴리 모니터링",
        "BMNR 관련 공시/실적 발표 일정 체크",
    ]

    if top_titles:
        summary.extend(top_titles)

    return FinalReport(
        request=request,
        generated_at=datetime.now(timezone.utc),
        executive_summary=summary,
        ranked_insights=ranked,
        bull_case=bull_case,
        bear_case=bear_case,
        action_points=action_points,
    )


def format_report(report: FinalReport) -> str:
    lines = [
        "# CryptoAgent Report",
        f"- Query: {report.request.raw_query}",
        f"- Assets: {', '.join(report.request.assets)}",
        f"- Window: {report.request.window_hours}h",
        "",
        "## Executive Summary",
    ]
    lines.extend(f"- {x}" for x in report.executive_summary)

    lines.append("\n## Ranked Insights")
    for item in report.ranked_insights:
        lines.append(f"- ({item.asset}) {item.grade} {item.score}: {item.title}")

    lines.append("\n## Bull Case")
    lines.extend(f"- {x}" for x in report.bull_case)

    lines.append("\n## Bear Case")
    lines.extend(f"- {x}" for x in report.bear_case)

    lines.append("\n## Action Points")
    lines.extend(f"- {x}" for x in report.action_points)

    return "\n".join(lines)
