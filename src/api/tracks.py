from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src import database, movie_database
from src.entities.user import User
from src.enums import UserRole
from src.query_params.track_remove import TrackRemove
from src.utils.auth import get_user

router = APIRouter()


@router.post("/remove-track")
def remove_track(params: TrackRemove, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if user.role != UserRole.OWNER:
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    track = movie_database.get_track(track_id=params.track_id)
    if track is None:
        return JSONResponse({"status": "error", "message": f"Не удалось найти трек с track_id = {params.track_id} в базе"})

    movie_database.remove_track(track_id=params.track_id, username=user.username)
    return JSONResponse({"status": "success"})


@router.get("/track-history/{track_id}")
def get_track_history(track_id: int) -> JSONResponse:
    history = list(database.history.find({"track_id": track_id}, {"_id": 0}).sort("timestamp", -1))
    return JSONResponse({"status": "success", "history": jsonable_encoder(history)})
