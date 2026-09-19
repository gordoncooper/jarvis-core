#!/usr/bin/env python3
"""jarvis.lan pulse stub. No LLM. House facts from noc collector only."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

START = time.time()
UI = Path(__file__).resolve().parent / "index.html"
PORT = int(os.environ.get("PORT", "8080"))
NOC_URL = os.environ.get("NOC_SNAPSHOT_URL", "http://jarvis-noc.apps.svc.cluster.local:8080/api/snapshot")


def noc_snapshot() -> dict | None:
    try:
        with urllib.request.urlopen(NOC_URL, timeout=3) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def pulse() -> dict:
    snap = noc_snapshot()
    if not snap:
        return {
            "ok": True,
            "service": "jarvis-core",
            "version": os.environ.get("CORE_VERSION", "v0.2.0"),
            "uptime_s": int(time.time() - START),
            "house": "degraded",
            "line": "house degraded · noc unreachable",
            "noc": False,
        }
    nodes = snap.get("nodes") or []
    ready = all(n.get("ready") for n in nodes) if nodes else False
    house = "ok" if ready and snap.get("kube") else "degraded"
    pods = (snap.get("pods") or {}).get("count", "?")
    return {
        "ok": True,
        "service": "jarvis-core",
        "version": os.environ.get("CORE_VERSION", "v0.2.0"),
        "uptime_s": int(time.time() - START),
        "house": house,
        "line": f"house {house} · pods {pods} · confirm 0",
        "noc": True,
        "nodes": nodes,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/health", "/healthz"):
            p = pulse()
            body = json.dumps(
                {"ok": True, "service": p["service"], "version": p["version"], "house": p["house"], "noc": p["noc"]}
            ).encode()
            self._send(200, body, "application/json")
            return
        if path == "/api/pulse":
            self._send(200, json.dumps(pulse()).encode(), "application/json")
            return
        if path in ("/", "/index.html"):
            html = UI.read_text() if UI.exists() else b"<h1>JARVIS</h1>"
            if isinstance(html, str):
                html = html.encode()
            self._send(200, html, "text/html; charset=utf-8")
            return
        self._send(404, b'{"ok":false}', "application/json")


if __name__ == "__main__":
    print(f"jarvis-core glass :{PORT} noc={NOC_URL}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
