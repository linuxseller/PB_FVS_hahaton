from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/decide")
def decide(state: dict):
    energy = state.get("resources", {}).get("energy", 0)
    tasks = state.get("available_tasks", [])

    feasible = [t for t in tasks if t.get("energy_cost", 0) <= energy]
    if not feasible:
        return {"action": "skip"}

    def value(t):
        reward = t.get("reward", 0)
        risk = t.get("risk", 0)
        duration = max(t.get("duration", 1), 1)
        return reward * (1 - risk) / duration

    best = max(feasible, key=value)
    return {"action": "accept", "task_id": best["id"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
