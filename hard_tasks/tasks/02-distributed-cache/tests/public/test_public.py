import os
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

TARGET = os.environ["TARGET_URL"]


class BackendHandler(BaseHTTPRequestHandler):
    store = {"hot": "42", "cold": "abc"}
    get_counter = 0
    delay = 0.15

    def do_GET(self):
        if not self.path.startswith("/value/"):
            self.send_response(404); self.end_headers(); return
        type(self).get_counter += 1
        time.sleep(type(self).delay)
        key = self.path.split("/")[-1]
        if key not in type(self).store:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"key": key, "value": type(self).store[key]}).encode())

    def do_POST(self):
        key = self.path.split("/")[-1]
        length = int(self.headers.get("content-length", "0"))
        data = json.loads(self.rfile.read(length) or b"{}")
        type(self).store[key] = data.get("value")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())

    def do_DELETE(self):
        key = self.path.split("/")[-1]
        type(self).store.pop(key, None)
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def start_backend():
    BackendHandler.store = {"hot": "42", "cold": "abc"}
    BackendHandler.get_counter = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), BackendHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


def test_health():
    assert requests.get(f"{TARGET}/health", timeout=2).status_code == 200


def test_cache_reduces_backend_calls():
    server, backend_url = start_backend()

    r = requests.post(f"{TARGET}/config", json={
        "backend_url": backend_url,
        "ttl_ms": 2000,
        "max_items": 10,
    }, timeout=3)
    assert r.status_code < 500

    values = []
    for _ in range(5):
        r = requests.get(f"{TARGET}/value/hot", timeout=3)
        assert r.status_code == 200
        values.append(r.json()["value"])

    assert values == ["42"] * 5
    assert BackendHandler.get_counter <= 2


def test_cache_invalidates_after_write():
    server, backend_url = start_backend()
    requests.post(f"{TARGET}/config", json={
        "backend_url": backend_url,
        "ttl_ms": 5000,
        "max_items": 10,
    }, timeout=3)

    r = requests.get(f"{TARGET}/value/hot", timeout=3)
    assert r.json()["value"] == "42"

    r = requests.post(f"{TARGET}/value/hot", json={"value": "99"}, timeout=3)
    assert r.status_code in (200, 201, 204)

    r = requests.get(f"{TARGET}/value/hot", timeout=3)
    assert r.status_code == 200
    assert r.json()["value"] == "99"
