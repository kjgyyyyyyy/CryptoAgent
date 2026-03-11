from __future__ import annotations

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .chat import ChatSession


class ChatHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, session: ChatSession, web_root: Path, **kwargs):
        self._session = session
        self._web_root = web_root
        super().__init__(*args, directory=str(web_root), **kwargs)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        payload = json.loads(body or b"{}")
        query = str(payload.get("query", "")).strip()

        if not query:
            self._send_json({"error": "query is required"}, status=400)
            return

        answer = self._session.ask(query)
        self._send_json({"answer": answer}, status=200)

    def _send_json(self, data: dict, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAgent web chat server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    web_root = Path(__file__).resolve().parent.parent / "web"
    session = ChatSession()

    handler = partial(ChatHandler, session=session, web_root=web_root)
    server = ThreadingHTTPServer((args.host, args.port), handler)

    print(f"Serving CryptoAgent chat at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
