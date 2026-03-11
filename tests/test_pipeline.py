from cryptoagent.parsing import parse_user_request
from cryptoagent.pipeline import run_agent
from cryptoagent.scoring import rank_insights
from cryptoagent.data_sources import DemoDataSource


def test_parse_korean_query_assets_and_window():
    req = parse_user_request("ETH랑 비트마인 일주일 상세 리포트")
    assert req.assets == ["ETH", "BMNR"]
    assert req.window_hours == 24 * 7
    assert req.report_type == "deep"


def test_rank_insights_sorted_descending():
    source = DemoDataSource()
    news = source.collect_news(["ETH", "BMNR"], 24)
    flows = source.collect_flows(["ETH", "BMNR"])
    onchain = source.collect_onchain(["ETH", "BMNR"])
    ranked = rank_insights(news, flows, onchain)
    assert ranked
    assert ranked[0].score >= ranked[-1].score


def test_run_agent_contains_sections():
    report = run_agent("ETH BMNR 오늘 브리프")
    assert "# CryptoAgent Report" in report
    assert "## Executive Summary" in report
    assert "## Ranked Insights" in report
