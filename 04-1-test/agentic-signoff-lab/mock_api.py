import json
from http.server import BaseHTTPRequestHandler, HTTPServer

ALLOWED_PRODUCTS = {"SCORE_8", "SCORE_10"}  # spec says others -> 400

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/v1/score-requests":
            return self._send(404, {"error": "not_found"})
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid_json"})
        for field in ("request_id", "client_id", "consumer_ref", "product"):
            if field not in body:
                return self._send(400, {"error": "missing_field", "field": field})
        # PLANTED BUG: unknown product is accepted instead of rejected with 400
        return self._send(201, {"request_id": body["request_id"], "status": "ACCEPTED", "score": 712})

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("mock API on http://127.0.0.1:8099")
    HTTPServer(("127.0.0.1", 8099), Handler).serve_forever()
