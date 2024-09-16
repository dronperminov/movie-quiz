from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.config import LOGGING_CONFIG

from src import database
from src.api import api, auth, movies, persons


def init_routers() -> None:
    app.include_router(api.router)
    app.include_router(auth.router)
    app.include_router(movies.router)
    app.include_router(persons.router)


def init_static_directories() -> None:
    app.mount("/styles", StaticFiles(directory="web/styles"))
    app.mount("/js", StaticFiles(directory="web/js"))
    app.mount("/fonts", StaticFiles(directory="web/fonts"))
    app.mount("/images", StaticFiles(directory="web/images"))
    app.mount("/profile-images", StaticFiles(directory="../plush-anvil/web/images/profiles"))


def init_logging_config() -> None:
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncContextManager[None]:
    database.connect()
    yield
    database.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=500)

init_routers()
init_static_directories()
init_logging_config()
