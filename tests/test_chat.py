from cryptoagent.chat import ChatSession
from cryptoagent.llm import OpenRouterClient


class FakeLLM(OpenRouterClient):
    def __init__(self):
        super().__init__(api_key="test-key")

    def chat(self, messages, temperature=0.3):
        assert messages
        return "LLM 응답: 질문 잘 받았고 데이터 기반으로 설명할게."


def test_chat_session_fallback_without_api_key():
    session = ChatSession(llm_client=OpenRouterClient(api_key=""))
    answer = session.ask("ETH 최근 24시간 수급 어때?")
    assert "로컬 응답" in answer
    assert "assets=ETH" in answer


def test_chat_session_uses_llm_when_available():
    session = ChatSession(llm_client=FakeLLM())
    answer = session.ask("ETH와 BMNR 수급 어떻노")
    assert answer.startswith("LLM 응답")


def test_chat_session_followup_inherits_window_when_missing():
    session = ChatSession(llm_client=OpenRouterClient(api_key=""))
    session.ask("ETH 7일 상세 리포트")
    follow = session.ask("그럼 BMNR은?")
    assert "window_hours=168" in follow
    assert "assets=BMNR" in follow
