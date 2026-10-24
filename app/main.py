import json
import time
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ChatRequest, ChatResponse
from app.llm import generate_reply, stream_reply
from app.config import settings

app = FastAPI(title="GenAI Chat", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- In-memory rate limiter ----------
RATE_LIMIT = 20
RATE_WINDOW = 60
_hits: dict[str, list[float]] = defaultdict(list)

def _check_rate_limit(ip: str) -> None:
    now = time.time()
    _hits[ip] = [t for t in _hits[ip] if now - t < RATE_WINDOW]
    if len(_hits[ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {RATE_LIMIT} req / {RATE_WINDOW}s.",
        )
    _hits[ip].append(now)


# ---------- Endpoints ----------

@app.get("/health")
async def health():
    model = (
        settings.OLLAMA_MODEL
        if settings.LLM_PROVIDER == "ollama"
        else settings.OPENAI_MODEL
    )
    return {"status": "ok", "provider": settings.LLM_PROVIDER, "model": model}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    _check_rate_limit(request.client.host)
    try:
        reply = await generate_reply(req.message, req.history, use_fast=req.use_fast)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    _check_rate_limit(request.client.host)

    async def event_gen():
        try:
            async for delta in stream_reply(req.message, req.history, use_fast=req.use_fast):
                yield f"data: {json.dumps({'delta': delta})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'{type(e).__name__}: {e}'})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------- Static UI ----------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def index():
    idx = "app/static/index.html"
    try:
        return FileResponse(idx)
    except FileNotFoundError:
        return {"message": "Hello from FastAPI 👋 (UI not built yet)"}
 
