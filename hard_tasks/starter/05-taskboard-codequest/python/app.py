from fastapi import FastAPI, Response
from datetime import datetime
import uvicorn

app = FastAPI()
users = {}
tasks = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/users")
def create_user(user: dict, response: Response):
    if user["role"] not in ["user", "admin"]:
        response.status_code = 400
        return {"error": "invalid role"}
    if user["id"] in users:
        response.status_code = 409
        return {"error": "user exists"}
    users[user["id"]] = user
    response.status_code = 201
    return user

@app.post("/tasks")
def create_task(task: dict, response: Response):
    if task["id"] in tasks:
        response.status_code = 409
        return {"error": "task exists"}
    if task["owner_id"] not in users:
        response.status_code = 400
        return {"error": "unknown owner"}
    if task["status"] not in ["todo", "in_progress", "done"]:
        response.status_code = 400
        return {"error": "invalid status"}
    datetime.fromisoformat(task["deadline"])
    tasks[task["id"]] = task
    response.status_code = 201
    return task

@app.get("/tasks/{task_id}")
def get_task(task_id: str, response: Response):
    if task_id not in tasks:
        response.status_code = 404
        return {"error": "not found"}
    return tasks[task_id]

@app.get("/tasks")
def list_tasks(status: str | None = None, owner_id: str | None = None):
    result = list(tasks.values())
    if status is not None:
        result = [t for t in result if t["status"] == status]
    if owner_id is not None:
        result = [t for t in result if t["owner_id"] == owner_id]
    return result

def can_modify(actor_id, task):
    actor = users.get(actor_id)
    if not actor:
        return False
    return actor["role"] == "admin" or task["owner_id"] == actor_id

@app.patch("/tasks/{task_id}")
def patch_task(task_id: str, data: dict, response: Response):
    if task_id not in tasks:
        response.status_code = 404
        return {"error": "not found"}
    task = tasks[task_id]
    if not can_modify(data.get("actor_id"), task):
        response.status_code = 403
        return {"error": "forbidden"}
    if "status" in data:
        if data["status"] not in ["todo", "in_progress", "done"]:
            response.status_code = 400
            return {"error": "invalid status"}
        task["status"] = data["status"]
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, data: dict, response: Response):
    if task_id not in tasks:
        response.status_code = 404
        return {"error": "not found"}
    task = tasks[task_id]
    if not can_modify(data.get("actor_id"), task):
        response.status_code = 403
        return {"error": "forbidden"}
    del tasks[task_id]
    return {"ok": True}

@app.get("/report")
def report(now: str):
    now_dt = datetime.fromisoformat(now)
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    overdue = 0
    for task in tasks.values():
        by_status[task["status"]] += 1
        deadline = datetime.fromisoformat(task["deadline"])
        if deadline < now_dt and task["status"] != "done":
            overdue += 1
    return {"total": len(tasks), "by_status": by_status, "overdue": overdue}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
