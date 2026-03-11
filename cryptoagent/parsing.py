from __future__ import annotations

import re
from typing import List

from .models import UserRequest


def _extract_assets(query: str) -> List[str]:
    text = query.lower()
    assets: List[str] = []
    if "eth" in text or "이더" in text:
        assets.append("ETH")
    if "bmnr" in text or "비트마인" in text:
        assets.append("BMNR")
    return assets or ["ETH", "BMNR"]


def _extract_window_hours(query: str) -> int:
    text = query.lower()
    if "30일" in text or "30d" in text:
        return 24 * 30
    if "7일" in text or "7d" in text or "일주일" in text:
        return 24 * 7
    if "1일" in text or "24시간" in text or "today" in text:
        return 24

    match = re.search(r"(\d+)\s*(시간|h)", text)
    if match:
        return max(1, int(match.group(1)))
    return 24


def parse_user_request(query: str) -> UserRequest:
    report_type = "deep" if any(k in query.lower() for k in ["딥", "deep", "상세"]) else "brief"
    return UserRequest(
        raw_query=query,
        assets=_extract_assets(query),
        window_hours=_extract_window_hours(query),
        report_type=report_type,
    )
