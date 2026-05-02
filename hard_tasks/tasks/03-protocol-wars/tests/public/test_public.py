import os
import requests

TARGET = os.environ["TARGET_URL"]


def checksum(s: str) -> int:
    return sum(ord(ch) for ch in s)


def send(mid, part, total, payload, bad=False):
    return requests.post(f"{TARGET}/ingest", json={
        "message_id": mid,
        "part": part,
        "total": total,
        "payload": payload,
        "checksum": checksum(payload) + (1 if bad else 0),
    }, timeout=2)


def test_health():
    assert requests.get(f"{TARGET}/health", timeout=2).status_code == 200


def test_assemble_out_of_order_message():
    send("m1", 2, 3, "LLO ")
    send("m1", 1, 3, "HE")
    r = send("m1", 3, 3, "WORLD")
    assert r.status_code == 200

    r = requests.get(f"{TARGET}/result/m1", timeout=2)
    data = r.json()
    assert data["status"] == "complete"
    assert data["text"] == "HELLO WORLD"


def test_ignore_corrupted_packet_then_accept_valid_packet():
    send("m2", 1, 2, "GOOD")
    send("m2", 2, 2, " DATA", bad=True)

    r = requests.get(f"{TARGET}/result/m2", timeout=2)
    assert r.json()["status"] == "pending"

    send("m2", 2, 2, " DATA")
    r = requests.get(f"{TARGET}/result/m2", timeout=2)
    data = r.json()
    assert data["status"] == "complete"
    assert data["text"] == "GOOD DATA"


def test_duplicates_do_not_break_result():
    send("m3", 1, 2, "A")
    send("m3", 1, 2, "A")
    send("m3", 2, 2, "B")
    send("m3", 2, 2, "B")

    r = requests.get(f"{TARGET}/result/m3", timeout=2)
    assert r.json()["text"] == "AB"
