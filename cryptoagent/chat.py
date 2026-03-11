from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .pipeline import run_agent
from .parsing import parse_user_request


@dataclass
class ChatMemory:
    last_assets: List[str] = field(default_factory=lambda: ["ETH", "BMNR"])
    last_time_window: int = 24
    last_report_type: str = "brief"


class ChatSession:
    """Simple conversational wrapper with lightweight context carry-over."""

    def __init__(self) -> None:
        self.memory = ChatMemory()

    def _is_follow_up(self, query: str) -> bool:
        followup_tokens = ["그럼", "그럼요", "그런데", "그럼 bmnr", "then", "what about", "다시"]
        q = query.lower()
        return any(token in q for token in followup_tokens)

    def _normalize_query(self, query: str) -> str:
        parsed = parse_user_request(query)
        if not self._is_follow_up(query):
            self.memory.last_assets = parsed.assets
            self.memory.last_time_window = parsed.window_hours
            self.memory.last_report_type = parsed.report_type
            return query

        has_asset_keyword = any(k in query.lower() for k in ["eth", "이더", "bmnr", "비트마인"])
        assets = parsed.assets if has_asset_keyword else self.memory.last_assets
        window_hours = parsed.window_hours if parsed.window_hours != 24 else self.memory.last_time_window

        asset_text = ", ".join(assets)
        style_text = "상세" if self.memory.last_report_type == "deep" else "브리프"

        normalized = f"{asset_text} {window_hours}시간 {style_text} 리포트. 사용자 질문: {query}"

        self.memory.last_assets = assets
        self.memory.last_time_window = window_hours
        return normalized

    def ask(self, query: str) -> str:
        normalized = self._normalize_query(query)
        return run_agent(normalized)
