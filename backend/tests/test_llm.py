import json
import socketserver
import threading
import unittest
from http.server import BaseHTTPRequestHandler

from app.services.llm import LLMClient, LLMError


class _OkHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        content = json.dumps(
            {"choices": [{"message": {"content": "MOCK-ANSWER for " + body.get("model", "?")}}]}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


class _ErrorHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        content = b'{"error": "invalid key"}'
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


class TestLLMClient(unittest.TestCase):
    @classmethod
    def _serve(cls, handler):
        srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        return srv, srv.server_address[1]

    def test_configured(self):
        self.assertTrue(LLMClient(base="http://x/v1", key="k", model="m").configured)
        self.assertFalse(LLMClient(base=None, model="m").configured)

    def test_chat_parses_content(self):
        srv, port = self._serve(_OkHandler)
        try:
            c = LLMClient(base=f"http://127.0.0.1:{port}/v1", key="k", model="mock-model")
            self.assertEqual(c.chat("sys", "user question"), "MOCK-ANSWER for mock-model")
        finally:
            srv.shutdown()
            srv.server_close()

    def test_chat_raises_when_unconfigured(self):
        with self.assertRaises(LLMError):
            LLMClient(base=None).chat("sys", "user")

    def test_chat_raises_on_http_error(self):
        srv, port = self._serve(_ErrorHandler)
        try:
            c = LLMClient(base=f"http://127.0.0.1:{port}/v1", key="bad", model="m")
            with self.assertRaises(LLMError) as ctx:
                c.chat("sys", "user")
            self.assertIn("401", str(ctx.exception))
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
