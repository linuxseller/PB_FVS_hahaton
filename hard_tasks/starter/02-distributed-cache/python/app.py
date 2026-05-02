from fastapi import FastAPI, Response
import requests
import time
import uvicorn

app = FastAPI()
backend_url = None
ttl_ms = 1000
max_items = 100
cache = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/config")
def config(data: dict):
    global backend_url, ttl_ms, max_items, cache
    backend_url = data["backend_url"]
    ttl_ms = data.get("ttl_ms", 1000)
    max_items = data.get("max_items", 100)
    cache = {}
    return {"ok": True}

def now_ms():
    return int(time.time() * 1000)

@app.get("/value/{key}")
def get_value(key: str, response: Response):
    item = cache.get(key)
    if item and now_ms() < item["expires_at"]:
        return {"key": key, "value": item["value"], "source": "cache"}

    r = requests.get(f"{backend_url}/value/{key}", timeout=3)
    if r.status_code != 200:
        response.status_code = r.status_code
        return {"error": "not found"}

    value = r.json()["value"]
    if len(cache) >= max_items:
        oldest = sorted(cache.items(), key=lambda x: x[1]["expires_at"])[0][0]
        cache.pop(oldest, None)
    cache[key] = {"value": value, "expires_at": now_ms() + ttl_ms}
    return {"key": key, "value": value, "source": "backend"}

@app.post("/value/{key}")
def set_value(key: str, data: dict):
    value = data.get("value")
    requests.post(f"{backend_url}/value/{key}", json={"value": value}, timeout=3)
    cache[key] = {"value": value, "expires_at": now_ms() + ttl_ms}
    return {"ok": True}

@app.delete("/value/{key}")
def delete_value(key: str):
    cache.pop(key, None)
    requests.delete(f"{backend_url}/value/{key}", timeout=3)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
