from __future__ import annotations

from .data_sources import DemoDataSource
from .parsing import parse_user_request
from .reporting import build_report, format_report
from .scoring import rank_insights


def run_agent(query: str) -> str:
    request = parse_user_request(query)
    source = DemoDataSource()

    prices = source.collect_prices(request.assets)
    news = source.collect_news(request.assets, request.window_hours)
    flows = source.collect_flows(request.assets)
    onchain = source.collect_onchain(request.assets)

    ranked = rank_insights(news, flows, onchain)
    report = build_report(request, prices, ranked, flows, onchain)
    return format_report(report)
