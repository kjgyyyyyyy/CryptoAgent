from cryptoagent.chat import ChatSession


def test_chat_session_returns_conversational_answer():
    session = ChatSession()
    answer = session.ask("ETH 최근 24시간 수급 어때?")
    assert "좋아," in answer
    assert "ETH ETF 순유입" in answer
    assert "내 해석" in answer
def test_chat_session_basic_response_contains_report():
    session = ChatSession()
    answer = session.ask("ETH 최근 24시간 요약")
    assert "# CryptoAgent Report" in answer
    assert "Assets: ETH" in answer


def test_chat_session_followup_inherits_window_when_missing():
    session = ChatSession()
    first = session.ask("ETH 7일 상세 리포트")
    assert "Window: 168h" in first

    follow = session.ask("그럼 BMNR은?")
    assert "BMNR" in follow
    assert "최근 168시간" in follow
    assert "Assets: BMNR" in follow
    assert "Window: 168h" in follow
