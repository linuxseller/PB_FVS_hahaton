import os
import time
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

TARGET = os.environ["TARGET_URL"]


class WorkerHandler(BaseHTTPRequestHandler):
    delay = 0.0
    fail = False
    counter = 0

    def do_POST(self):
        if self.path != "/work":
            self.send_response(404)
            self.end_headers()
            return

        type(self).counter += 1
        time.sleep(type(self).delay)

        if type(self).fail:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"status":"error"}')
            return

        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {
            "status": "ok",
            "result": "processed:" + str(body.get("payload", "")),
        }
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        pass


def start_worker(delay=0.0, fail=False):
    class CustomWorker(WorkerHandler):
        pass

    CustomWorker.delay = delay
    CustomWorker.fail = fail
    CustomWorker.counter = 0

    server = ThreadingHTTPServer(("127.0.0.1", 0), CustomWorker)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, CustomWorker, f"http://127.0.0.1:{port}"


def test_health():
    r = requests.get(f"{TARGET}/health", timeout=2)
    assert r.status_code == 200


def test_balancer_handles_basic_requests():
    server1, cls1, url1 = start_worker()
    server2, cls2, url2 = start_worker()

    r = requests.post(f"{TARGET}/config", json={
        "workers": [
            {"id": "w1", "url": url1},
            {"id": "w2", "url": url2},
        ]
    }, timeout=3)
    assert r.status_code < 500

    ok = 0
    for i in range(10):
        r = requests.post(f"{TARGET}/handle", json={
            "request_id": f"r{i}",
            "payload": f"data-{i}",
            "timeout_ms": 800,
        }, timeout=2)
        assert r.status_code == 200
        data = r.json()
        assert data["request_id"] == f"r{i}"
        if data.get("status") == "ok":
            ok += 1
            assert data.get("worker") in ["w1", "w2"]

    assert ok >= 8


def test_balancer_avoids_always_failing_worker():
    bad_server, bad_cls, bad_url = start_worker(fail=True)
    good_server, good_cls, good_url = start_worker(fail=False)

    r = requests.post(f"{TARGET}/config", json={
        "workers": [
            {"id": "bad", "url": bad_url},
            {"id": "good", "url": good_url},
        ]
    }, timeout=3)
    assert r.status_code < 500

    ok = 0
    for i in range(12):
        r = requests.post(f"{TARGET}/handle", json={
            "request_id": f"x{i}",
            "payload": "x",
            "timeout_ms": 800,
        }, timeout=3)
        assert r.status_code == 200
        if r.json().get("status") == "ok":
            ok += 1

    assert ok >= 8
    assert good_cls.counter >= 8
