#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WPS OAuth 回调接收服务：监听 127.0.0.1:9999，捕获授权 code 并保存到 /tmp/wps_oauth_code.json
用法:
  1) terminal(background=true): python3 wps_callback_server.py
  2) 自测: curl "http://localhost:9999/callback?code=test123&state=x" -o /dev/null
  3) 用户授权后浏览器跳回 localhost:9999，读 /tmp/wps_oauth_code.json 拿 code
"""
import http.server
import urllib.parse
import json
import sys

SAVE_PATH = "/tmp/wps_oauth_code.json"

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        data = {"code": code, "state": state, "full_path": self.path}
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, ensure_ascii=False)
        body = ("<html><body style='font-family:sans-serif;padding:40px;'>"
                "<h2>✅ 授权回调已捕获</h2>"
                f"<p>code: <code>{code}</code></p>"
                f"<p>state: {state}</p>"
                "<p>现在可以回到 Hermes 继续操作了。</p></body></html>").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[oauth-callback] {fmt % args}\n")

if __name__ == "__main__":
    port = 9999
    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    print(f"WPS OAuth callback listening on http://localhost:{port}/callback", flush=True)
    server.serve_forever()
