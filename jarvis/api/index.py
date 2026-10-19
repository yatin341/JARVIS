
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Jarvis AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Jarvis API is running"
    }

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/state")
def state():
    return {
        "state": "idle",
        "heard": "",
        "text": ""
    }
