"""
Python HTTP Server cho Hệ thống AI Agent Xử lý Cơ hội Bán hàng B2B - Minh An
Chạy tại: http://localhost:8080/
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler


class AgentRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            with open("web/index.html", "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/status":
            payload = json.dumps({"status": "online", "port": 8080}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/save-batch":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            os.makedirs("outputs/dossiers", exist_ok=True)
            os.makedirs("outputs/drafts", exist_ok=True)
            for opp in data.get("opportunities", []):
                inq_id = opp.get("inquiry_id", "REQ")
                if opp.get("dossier_md"):
                    with open(f"outputs/dossiers/dossier_{inq_id}.md", "w", encoding="utf-8") as f:
                        f.write(opp["dossier_md"])
                if opp.get("draft_response"):
                    with open(f"outputs/drafts/draft_response_{inq_id}.txt", "w", encoding="utf-8") as f:
                        f.write(opp["draft_response"])
                if opp.get("approval_ticket"):
                    with open(f"outputs/drafts/approval_ticket_{inq_id}.txt", "w", encoding="utf-8") as f:
                        f.write(opp["approval_ticket"])
            resp = json.dumps({"saved": True}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(resp)


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), AgentRequestHandler)
    print("🚀 Minh An B2B AI Agent Server đang chạy tại: http://localhost:8080/")
    server.serve_forever()

