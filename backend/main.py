"""
Single deployable entry point: serves the API routes AND the built
frontend from one process. Run with:

    uvicorn backend.main:app --reload

Frontend: build your frontend (e.g. `npm run build`) into frontend/dist
and it gets served as static files below. Until that build exists, the
API still works standalone (e.g. for testing with curl or the docs UI).
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import extract, status, chat

app = FastAPI(title="SDG Platform")

# Same-origin in production (single deployable) — CORS is only relevant
# if you run the frontend dev server separately during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust to your frontend dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extract.router)
app.include_router(status.router)
app.include_router(chat.router)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")