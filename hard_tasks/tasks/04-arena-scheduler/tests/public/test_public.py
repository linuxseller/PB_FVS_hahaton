import os
import requests

TARGET = os.environ["TARGET_URL"]


def decide(state):
    r = requests.post(f"{TARGET}/decide", json=state, timeout=2)
    assert r.status_code == 200
    return r.json()


def test_health():
    assert requests.get(f"{TARGET}/health", timeout=2).status_code == 200


def test_returns_valid_action():
    state = {
        "tick": 1,
        "resources": {"energy": 10, "workers": 1, "budget": 100},
        "active_tasks": [],
        "available_tasks": [
            {"id": "t1", "reward": 30, "duration": 2, "deadline_tick": 5, "energy_cost": 2, "risk": 0.1}
        ],
    }
    action = decide(state)
    assert action.get("action") in ["accept", "skip"]
    if action["action"] == "accept":
        assert action.get("task_id") == "t1"


def test_does_not_accept_impossible_task():
    state = {
        "tick": 1,
        "resources": {"energy": 1, "workers": 1, "budget": 100},
        "active_tasks": [],
        "available_tasks": [
            {"id": "expensive", "reward": 1000, "duration": 1, "deadline_tick": 3, "energy_cost": 5, "risk": 0.1}
        ],
    }
    action = decide(state)
    assert not (action.get("action") == "accept" and action.get("task_id") == "expensive")


def test_prefers_high_value_feasible_task():
    state = {
        "tick": 1,
        "resources": {"energy": 10, "workers": 1, "budget": 100},
        "active_tasks": [],
        "available_tasks": [
            {"id": "bad", "reward": 10, "duration": 4, "deadline_tick": 5, "energy_cost": 2, "risk": 0.4},
            {"id": "good", "reward": 100, "duration": 1, "deadline_tick": 4, "energy_cost": 2, "risk": 0.05}
        ],
    }
    action = decide(state)
    assert action.get("action") == "accept"
    assert action.get("task_id") == "good"
