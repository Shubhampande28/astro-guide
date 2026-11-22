"""FastAPI entrypoint for the Jyotish Guru backend."""

from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(title="Jyotish Guru API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by Docker Compose and CI."""
    return {"status": "ok", "env": settings.env}
