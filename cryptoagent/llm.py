from __future__ import annotations

import json
import os
from typing import List, Optional
from urllib import error, request

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout_sec: int = 45) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.timeout_sec = timeout_sec

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[dict], temperature: float = 0.3) -> str:
        if not self.enabled:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        req = request.Request(
            OPENROUTER_URL,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://local.cryptoagent",
                "X-Title": "CryptoAgent",
            },
        )

        try:
            with request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenRouter HTTPError {exc.code}: {detail}") from exc
        except Exception as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
