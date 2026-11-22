"""FastAPI entrypoint for the Jyotish Guru backend."""

from fastapi import FastAPI

from app.astro.router import router as chart_router
from app.chat.router import router as chat_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="Jyotish Guru API", version="0.1.0")
app.include_router(chart_router)
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by Docker Compose and CI."""
    return {"status": "ok", "env": settings.env}
