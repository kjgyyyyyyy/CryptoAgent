from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .data_sources import DemoDataSource
from .llm import OpenRouterClient
from .parsing import parse_user_request
from .pipeline import run_agent
from .scoring import rank_insights


@dataclass
class ChatMemory:
    last_assets: List[str] = field(default_factory=lambda: ["ETH", "BMNR"])
    last_time_window: int = 24
    last_report_type: str = "brief"
    history: List[Tuple[str, str]] = field(default_factory=list)


class ChatSession:
    """Conversational agent wrapper with optional OpenRouter LLM responses."""

    def __init__(self, llm_client: OpenRouterClient | None = None) -> None:
        self.memory = ChatMemory()
        self.source = DemoDataSource()
        self.llm = llm_client or OpenRouterClient()

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
            has_window = ("시간" in query) or ("일" in query) or ("d" in query.lower())
            window_hours = parsed.window_hours if has_window else self.memory.last_time_window
            has_style = any(k in query.lower() for k in ["상세", "딥", "deep", "브리프"])
            report_type = parsed.report_type if has_style else self.memory.last_report_type
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

    def _build_data_brief(self, req, intent: str) -> str:
        prices = self.source.collect_prices(req.assets)
        news = self.source.collect_news(req.assets, req.window_hours)
        flows = self.source.collect_flows(req.assets)
        onchain = self.source.collect_onchain(req.assets)
        ranked = rank_insights(news, flows, onchain)

        flow_map = self._metric_map(flows)
        onchain_map = self._metric_map(onchain)

        lines: List[str] = [
            f"assets={','.join(req.assets)}",
            f"window_hours={req.window_hours}",
            f"intent={intent}",
            "prices:",
        ]
        for p in prices:
            lines.append(f"- {p.asset}: price={p.price}, change_24h_pct={p.change_24h_pct}, volume_24h={p.volume_24h}")

        lines.append("flows:")
        for key, val in flow_map.items():
            lines.append(f"- {key}={val}")

        lines.append("onchain:")
        for key, val in onchain_map.items():
            lines.append(f"- {key}={val}")

        lines.append("top_ranked_news:")
        for item in ranked[:3]:
            lines.append(f"- ({item.asset}) {item.title} [grade={item.grade}, score={item.score}]")
        return "\n".join(lines)

    def _fallback_answer(self, query: str, req, intent: str) -> str:
        if intent == "report":
            return run_agent(f"{', '.join(req.assets)} {req.window_hours}시간 {req.report_type} 리포트")

        brief = self._build_data_brief(req, intent)
        return (
            f"LLM 연결 전/실패로 로컬 응답을 사용해.\n"
            f"요청: {query}\n\n"
            f"{brief}\n\n"
            "원하면 OPENROUTER_API_KEY 설정 후 더 자연스러운 대화형 답변으로 전환할 수 있어."
        )

    def _llm_answer(self, query: str, req, intent: str) -> str:
        data_brief = self._build_data_brief(req, intent)

        system_prompt = (
            "너는 개인 크립토 리서치 에이전트다. 한국어로 답하고, 말투는 자연스러운 대화형으로 유지한다. "
            "반드시 제공된 데이터 요약만 근거로 사용하며, 모르면 모른다고 말해라. "
            "투자 자문처럼 단정하지 말고 시나리오/리스크를 함께 말해라."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for user_text, assistant_text in self.memory.history[-3:]:
            messages.append({"role": "user", "content": user_text})
            messages.append({"role": "assistant", "content": assistant_text})

        messages.append(
            {
                "role": "user",
                "content": (
                    f"사용자 질문: {query}\n"
                    f"의도: {intent}\n"
                    f"현재 데이터:\n{data_brief}\n\n"
                    "요구사항: 1) 핵심 답변 2) 근거 2~4개 3) 해석/리스크 4) 다음에 물어볼만한 후속질문 1개"
                ),
            }
        )

        return self.llm.chat(messages)

    def ask(self, query: str) -> str:
        req = self._resolve_request(query)
        intent = self._intent(query)

        try:
            if self.llm.enabled:
                answer = self._llm_answer(query, req, intent)
            else:
                answer = self._fallback_answer(query, req, intent)
        except Exception:
            answer = self._fallback_answer(query, req, intent)

        self.memory.history.append((query, answer))
        return answer
