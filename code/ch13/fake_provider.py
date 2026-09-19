"""A provider-shaped HTTP server, so every listing here runs with no key.

The rule this book inherits from its companion volume is that a stage's
tests pass with no network, no database server and no model. A chapter
about model SDKs looks like the one place that cannot hold, and it is not:
an SDK talks HTTP, so a server on localhost that answers in the shape the
SDK expects is indistinguishable from a provider as far as the SDK is
concerned. Point the client's `base_url` at it and every other listing in
this chapter is a real SDK call over a real socket.

What it does NOT do is pretend to be a model. It echoes a fixed answer.
That is the point: the listings here are about the shape of the call, and a
shape is exactly what a fixed answer lets you check.

Run it on its own to see the answer it gives:

    cd code && uv run python ch13/fake_provider.py
"""

from __future__ import annotations

import json
import threading
from collections.abc import Generator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

# The answer every request gets back, as the JSON a structured output
# carries. Fixed, so a test can assert on it.
ANSWER: dict[str, Any] = {
    "summary": "disk filled up on the billing worker",
    "severity": 2,
    "needs_human": False,
}

INPUT_TOKENS = 41
OUTPUT_TOKENS = 17


def _response_body(text: str) -> dict[str, Any]:
    """One completed response, in the wire shape the SDK parses."""
    return {
        "id": "resp_fake",
        "object": "response",
        "created_at": 0,
        "model": "fake-provider",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "id": "msg_fake",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                        "annotations": [],
                    }
                ],
            }
        ],
        "usage": {
            "input_tokens": INPUT_TOKENS,
            "output_tokens": OUTPUT_TOKENS,
            "total_tokens": INPUT_TOKENS + OUTPUT_TOKENS,
        },
    }


class _Handler(BaseHTTPRequestHandler):
    """Answers any POST with the one response above."""

    def do_POST(self) -> None:  # noqa: N802  (http.server names it)
        length = int(self.headers.get("content-length", 0))
        self.rfile.read(length)
        raw = json.dumps(_response_body(json.dumps(ANSWER))).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Silence. The default writes every request to stderr, and a
        listing that writes to stderr fails this book's own listing test.
        The parameter keeps the base class's name, shadowing a builtin,
        because an override that renames it is a different method."""


@contextmanager
def fake_provider() -> Generator[str]:
    """Run the server on a free port and yield the base URL to point at."""
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/v1"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def main() -> int:
    import httpx

    with fake_provider() as base_url:
        # httpx, not the SDK: this file is the socket, and the next
        # listing is the SDK on top of it.
        reply = httpx.post(f"{base_url}/responses", json={}, timeout=5.0)
        body = reply.json()
    print(f"status      {reply.status_code}")
    print(f"model       {body['model']}")
    print(f"text        {body['output'][0]['content'][0]['text']}")
    print(f"usage       {body['usage']['total_tokens']} tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
