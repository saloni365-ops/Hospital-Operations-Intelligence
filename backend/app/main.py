"""ASGI application entrypoint for the hospital operations simulator."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="Adaptive Healthcare Operations Intelligence Platform",
    description="Research simulator for hospital capacity planning and allocation.",
    version="0.1.0",
)
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}
