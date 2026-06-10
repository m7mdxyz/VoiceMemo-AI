import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.admin.routes import router as admin_router
from app.auth.routes import router as auth_router
from app.auth.utils import seed_admin_user
from app.database import AsyncSessionLocal, init_db
from app.memos.routes import router as memos_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize the database schema and seed the admin user on startup."""
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_admin_user(db)
    yield


app = FastAPI(title="VoiceMemo AI", lifespan=lifespan)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Adds an X-Process-Time header (in seconds) to every response."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response


app.add_middleware(ProcessTimeMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(memos_router)
app.include_router(admin_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "Welcome to VoiceMemo AI"}
