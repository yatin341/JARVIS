from fastapi import FastAPI

app = FastAPI(title="Jarvis AI")

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Jarvis API is running on Render"
    }

@app.get("/api/health")
def health():
    return {"ok": True}
