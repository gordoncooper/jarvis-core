#!/usr/bin/env python3
"""jarvis-noc v0.1 — health + snapshot. No LLM. No jarvis-core."""
from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

START = time.time()
UI = Path(__file__).resolve().parent.parent / "ui" / "index.html"
PORT = int(os.environ.get("PORT", "8080"))

TOKEN_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
CA_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
NS_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")


def kube_get(path: str) -> dict | None:
    host = os.environ.get("KUBERNETES_SERVICE_HOST")
    port = os.environ.get("KUBERNETES_SERVICE_PORT", "443")
    if not host or not TOKEN_PATH.exists():
        return None
    token = TOKEN_PATH.read_text().strip()
    ctx = ssl.create_default_context(cafile=str(CA_PATH))
    req = urllib.request.Request(
        f"https://{host}:{port}{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def snapshot() -> dict:
    now = time.time()
    nodes_raw = kube_get("/api/v1/nodes")
    pods_raw = kube_get("/api/v1/pods")
    nodes = []
    if nodes_raw and "items" in nodes_raw:
        for n in nodes_raw["items"]:
            name = n["metadata"]["name"]
            labels = n["metadata"].get("labels", {})
            conds = {c["type"]: c["status"] for c in n["status"].get("conditions", [])}
            nodes.append(
                {
                    "name": name,
                    "role": labels.get("jarvis.role", labels.get("kubernetes.io/hostname", "?")),
                    "ready": conds.get("Ready") == "True",
                }
            )
    pod_count = 0
    not_ready = 0
    if pods_raw and "items" in pods_raw:
        pod_count = len(pods_raw["items"])
        for p in pods_raw["items"]:
            phase = p.get("status", {}).get("phase", "")
            if phase not in ("Running", "Succeeded"):
                not_ready += 1
    kube = nodes_raw is not None
    return {
        "ok": True,
        "service": "jarvis-noc",
        "version": os.environ.get("NOC_VERSION", "v0.1.0"),
        "uptime_s": int(now - START),
        "kube": kube,
        "namespace": NS_PATH.read_text().strip() if NS_PATH.exists() else None,
        "nodes": nodes,
        "pods": {"count": pod_count, "not_ready": not_ready},
        "note": "collector only. inference down must not kill this process.",
    }


HTML_FALLBACK = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>NOC</title>
<style>
body{margin:0;background:#07090b;color:#d8e0e8;font:14px/1.4 ui-monospace,monospace}
main{max-width:720px;margin:12vh auto;padding:0 24px}
h1{color:#5eead4;font-weight:500;letter-spacing:.12em}
.ok{color:#5eead4}.bad{color:#f59e0b}
a{color:#5eead4}
</style></head><body><main>
<h1>NOC</h1>
<p class="ok">jarvis-noc /health is up.</p>
<p>This glass does not require inference.</p>
</main></body></html>
"""


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
            snap = snapshot()
            body = json.dumps(
                {
                    "ok": True,
                    "service": snap["service"],
                    "version": snap["version"],
                    "kube": snap["kube"],
                    "uptime_s": snap["uptime_s"],
                }
            ).encode()
            self._send(200, body, "application/json")
            return
        if path == "/api/snapshot":
            body = json.dumps(snapshot()).encode()
            self._send(200, body, "application/json")
            return
        if path in ("/", "/index.html"):
            html = UI.read_text() if UI.exists() else HTML_FALLBACK
            self._send(200, html.encode(), "text/html; charset=utf-8")
            return
        self._send(404, b'{"ok":false,"error":"not found"}', "application/json")


def main():
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"jarvis-noc listening :{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
