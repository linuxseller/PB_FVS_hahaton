from fastapi import FastAPI
import uvicorn

app = FastAPI()
messages = {}

@app.get("/health")
def health():
    return {"status": "ok"}

def checksum(s: str) -> int:
    return sum(ord(ch) for ch in s)

@app.post("/ingest")
def ingest(packet: dict):
    mid = packet["message_id"]
    part = int(packet["part"])
    total = int(packet["total"])
    payload = packet["payload"]

    if checksum(payload) != int(packet["checksum"]):
        return {"accepted": False, "complete": False}

    msg = messages.setdefault(mid, {"total": total, "parts": {}})
    msg["total"] = total
    msg["parts"][part] = payload
    complete = len(msg["parts"]) == msg["total"]
    return {"accepted": True, "complete": complete}

@app.get("/result/{message_id}")
def result(message_id: str):
    msg = messages.get(message_id)
    if not msg or len(msg["parts"]) != msg["total"]:
        return {"message_id": message_id, "status": "pending", "text": None}
    text = "".join(msg["parts"][i] for i in range(1, msg["total"] + 1))
    return {"message_id": message_id, "status": "complete", "text": text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
