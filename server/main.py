from contextlib import asynccontextmanager
from fastapi import FastAPI
from server.routes import chat, providers
from server.database import init_db
from server.services.scheduler import start_scheduler, stop_scheduler
from server.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await start_scheduler()
    yield
    # Shutdown
    await stop_scheduler()


app = FastAPI(
    title="Prism Console 144",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(chat.router)
app.include_router(providers.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "prism-console-144"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
