import os
import requests

TARGET = os.environ["TARGET_URL"]


def test_health():
    assert requests.get(f"{TARGET}/health", timeout=2).status_code == 200


def test_create_users_and_tasks_and_filter():
    r = requests.post(f"{TARGET}/users", json={"id": "u1", "name": "Anna", "role": "user"}, timeout=2)
    assert r.status_code in (200, 201)

    r = requests.post(f"{TARGET}/users", json={"id": "admin", "name": "Root", "role": "admin"}, timeout=2)
    assert r.status_code in (200, 201)

    r = requests.post(f"{TARGET}/tasks", json={
        "id": "t1",
        "title": "Fix bug",
        "owner_id": "u1",
        "status": "todo",
        "deadline": "2026-05-01T12:00:00",
    }, timeout=2)
    assert r.status_code in (200, 201)

    r = requests.get(f"{TARGET}/tasks/t1", timeout=2)
    assert r.status_code == 200
    assert r.json()["owner_id"] == "u1"

    r = requests.get(f"{TARGET}/tasks?status=todo&owner_id=u1", timeout=2)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(t["id"] == "t1" for t in data)


def test_permissions_and_report():
    # Tests may run after previous test in same service, so use unique ids.
    requests.post(f"{TARGET}/users", json={"id": "u2", "name": "Bob", "role": "user"}, timeout=2)
    requests.post(f"{TARGET}/users", json={"id": "u3", "name": "Carol", "role": "user"}, timeout=2)
    requests.post(f"{TARGET}/users", json={"id": "admin2", "name": "Admin", "role": "admin"}, timeout=2)

    requests.post(f"{TARGET}/tasks", json={
        "id": "t2",
        "title": "Late task",
        "owner_id": "u2",
        "status": "todo",
        "deadline": "2026-05-01T10:00:00",
    }, timeout=2)

    r = requests.patch(f"{TARGET}/tasks/t2", json={"actor_id": "u3", "status": "done"}, timeout=2)
    assert r.status_code in (403, 401)

    r = requests.patch(f"{TARGET}/tasks/t2", json={"actor_id": "u2", "status": "in_progress"}, timeout=2)
    assert r.status_code == 200

    r = requests.get(f"{TARGET}/report?now=2026-05-01T13:00:00", timeout=2)
    assert r.status_code == 200
    report = r.json()
    assert report["total"] >= 1
    assert report["overdue"] >= 1

    r = requests.delete(f"{TARGET}/tasks/t2", json={"actor_id": "admin2"}, timeout=2)
    assert r.status_code in (200, 204)
