from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import ALLOWED_ORIGINS

app = FastAPI(title="Ask Hume", version="0.1.0")

# CORS — only allow configured origins (never use allow_origins=["*"] in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    # Browser blocks custom response headers by default; expose the ones the
    # frontend needs to read (session continuity + transcript display).
    expose_headers=["X-Session-Id", "X-Transcript", "X-Reply"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
