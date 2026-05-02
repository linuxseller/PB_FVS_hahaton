from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()
workers = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/config")
def config(data: dict):
    global workers
    workers = data.get("workers", [])
    return {"ok": True, "workers": len(workers)}

@app.post("/handle")
def handle(req: dict):
    timeout = req.get("timeout_ms", 800) / 1000
    for worker in workers:
        try:
            r = requests.post(worker["url"] + "/work", json=req, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "ok":
                    return {
                        "request_id": req.get("request_id"),
                        "status": "ok",
                        "worker": worker["id"],
                        "result": data.get("result"),
                    }
        except Exception:
            pass
    return {"request_id": req.get("request_id"), "status": "failed", "worker": None, "result": None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
