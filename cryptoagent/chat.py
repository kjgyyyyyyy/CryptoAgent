from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .data_sources import DemoDataSource
from .parsing import parse_user_request
from .pipeline import run_agent
from .scoring import rank_insights


@dataclass
class ChatMemory:
    last_assets: List[str] = field(default_factory=lambda: ["ETH", "BMNR"])
    last_time_window: int = 24
    last_report_type: str = "brief"
    last_topics: List[str] = field(default_factory=list)


class ChatSession:
    """Conversational agent wrapper with memory + intent-aware responses."""

    def __init__(self) -> None:
        self.memory = ChatMemory()
        self.source = DemoDataSource()

    def _is_follow_up(self, query: str) -> bool:
        q = query.lower()
        followup_tokens = ["그럼", "그런데", "그럼요", "what about", "then", "추가", "이어서", "다시"]
        return any(token in q for token in followup_tokens)

    def _intent(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["리포트", "보고서", "정리본", "전체"]):
            return "report"
        if any(k in q for k in ["수급", "flow", "etf", "기관"]):
            return "flow"
        if any(k in q for k in ["온체인", "지갑", "active", "staking", "체인"]):
            return "onchain"
        if any(k in q for k in ["뉴스", "기사", "이슈", "내러티브", "narrative"]):
            return "news"
        return "chat"

    def _resolve_request(self, query: str):
        parsed = parse_user_request(query)
        has_asset_keyword = any(k in query.lower() for k in ["eth", "이더", "bmnr", "비트마인"])

        if self._is_follow_up(query):
            assets = parsed.assets if has_asset_keyword else self.memory.last_assets
            window_hours = parsed.window_hours if ("시간" in query or "일" in query or "d" in query.lower()) else self.memory.last_time_window
            report_type = parsed.report_type if any(k in query.lower() for k in ["상세", "딥", "deep", "브리프"]) else self.memory.last_report_type
            parsed.assets = assets
            parsed.window_hours = window_hours
            parsed.report_type = report_type

        self.memory.last_assets = parsed.assets
        self.memory.last_time_window = parsed.window_hours
        self.memory.last_report_type = parsed.report_type
        return parsed

    @staticmethod
    def _metric_map(rows) -> Dict[str, float]:
        return {f"{x.asset}:{x.metric}": x.value for x in rows}

    def _conversation_answer(self, query: str) -> str:
        req = self._resolve_request(query)
        intent = self._intent(query)

        prices = self.source.collect_prices(req.assets)
        news = self.source.collect_news(req.assets, req.window_hours)
        flows = self.source.collect_flows(req.assets)
        onchain = self.source.collect_onchain(req.assets)
        ranked = rank_insights(news, flows, onchain)

        if intent == "report":
            return run_agent(f"{', '.join(req.assets)} {req.window_hours}시간 {req.report_type} 리포트")

        flow_map = self._metric_map(flows)
        onchain_map = self._metric_map(onchain)

        lead = f"좋아, {', '.join(req.assets)} 기준으로 최근 {req.window_hours}시간 데이터 빠르게 볼게."
        lines: List[str] = [lead]

        for p in prices:
            direction = "상승" if p.change_24h_pct >= 0 else "하락"
            lines.append(f"- {p.asset} 가격: ${p.price:,.2f} ({p.change_24h_pct:+.2f}%, {direction})")

        if intent in {"flow", "chat"}:
            if "ETH:etf_netflow_usd" in flow_map:
                lines.append(f"- ETH ETF 순유입: ${flow_map['ETH:etf_netflow_usd']:,.0f}")
            if "ETH:exchange_netflow_eth" in flow_map:
                flow_val = flow_map["ETH:exchange_netflow_eth"]
                signal = "순유출(매도압력 완화 가능)" if flow_val < 0 else "순유입(매도압력 경계)"
                lines.append(f"- 거래소 ETH 플로우: {flow_val:,.0f} ETH ({signal})")
            if "BMNR:institutional_interest_index" in flow_map:
                lines.append(f"- BMNR 기관 관심도 지수: {flow_map['BMNR:institutional_interest_index']:.1f}")

        if intent in {"onchain", "chat"}:
            if "ETH:active_addresses_24h" in onchain_map:
                lines.append(f"- ETH 활성 주소: {onchain_map['ETH:active_addresses_24h']:,.0f}")
            if "ETH:staking_net_change_eth" in onchain_map:
                lines.append(f"- ETH 스테이킹 순증감: {onchain_map['ETH:staking_net_change_eth']:,.0f} ETH")

        if intent in {"news", "chat"} and ranked:
            lines.append("- 주목 이슈 TOP2:")
            for item in ranked[:2]:
                lines.append(f"  • ({item.asset}) {item.title} [중요도 {item.grade}/{item.score}]")

        lines.append("\n내 해석:")
        if "ETH:exchange_netflow_eth" in flow_map and flow_map["ETH:exchange_netflow_eth"] < 0:
            lines.append("- ETH는 ETF 유입 + 거래소 순유출 조합이라 단기 수급은 비교적 우호적이야.")
        if any(p.asset == "BMNR" and p.change_24h_pct < 0 for p in prices):
            lines.append("- BMNR은 가격이 약한데, 기사 모멘텀 대비 실제 실적/공시 확인이 중요해 보여.")

        lines.append("\n원하면 다음으로 ①7일 추세 비교 ②Bull/Base/Bear 시나리오 ③리스크 체크리스트 중 하나로 이어서 볼게.")

        self.memory.last_topics = [intent]
        return "\n".join(lines)

    def ask(self, query: str) -> str:
        return self._conversation_answer(query)
