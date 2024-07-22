from contextlib import asynccontextmanager
from pathlib import Path

import dotenv
import openai
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

from src.logger import get_logger
from src.schemas import AsyncResponse, MakeShortsInput
from src.tasks import make_shorts as async_make_shorts
from src.worker import broker, result_backend

dotenv.load_dotenv()

logger = get_logger("app")


@asynccontextmanager
async def fastapi_lifespan(app: FastAPI):
    logger.info("Starting FastAPI")
    await broker.startup()
    try:
        yield
    finally:
        await broker.shutdown()
    logger.info("FastAPI stopped")


app = FastAPI(
    title="Shorts cutter",
    description="This is a simple API to cut long YouTube video into multiple YouTube shorts.",
    version="0.1.0",
    debug=True,
    lifespan=fastapi_lifespan,
)

Path("static", "input").mkdir(parents=True, exist_ok=True)
Path("static", "output").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

openai_client = openai.Client()


@app.post("/")
async def create_task(data: MakeShortsInput):
    task = await async_make_shorts.kiq(data)
    return {"task_id": task.task_id}


@app.get("/{task_id}", response_model=AsyncResponse)
async def get_task(task_id: str):
    if await result_backend.is_result_ready(task_id):
        return await result_backend.get_result(task_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not ready"
    )
