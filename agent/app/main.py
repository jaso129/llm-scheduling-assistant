from fastapi import FastAPI
from app.api.agent_router import router as agent_router

app = FastAPI(title="LLM Agent Serving", version="0.4.0")

app.include_router(agent_router)

@app.get("/health")
def health():
    return {"ok": True}