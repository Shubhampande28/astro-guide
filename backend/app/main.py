"""FastAPI entrypoint for the Jyotish Guru backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.accounts.router import auth_router, me_router, profiles_router
from app.astro.router import router as chart_router
from app.chat.router import router as chat_router
from app.config import get_settings
from app.db import Base, get_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tables are created here rather than via Alembic migrations for now;
    # see DECISIONS.md.
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Jyotish Guru API", version="0.1.0", lifespan=lifespan)
app.include_router(chart_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(me_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by Docker Compose and CI."""
    return {"status": "ok", "env": settings.env}
