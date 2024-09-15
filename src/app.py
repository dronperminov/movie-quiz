from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI

from src import database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncContextManager[None]:
    database.connect()
    yield
    database.close()


app = FastAPI(lifespan=lifespan)
