from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from src import database, kinopoisk_parser, movie_database, quiz_tours_database, yandex_music_parser
from src.api import templates
from src.entities.user import User
from src.enums import UserRole
from src.query_params.direct_link import DirectLink
from src.query_params.history_query import HistoryQuery
from src.query_params.movie_parse import MovieParse
from src.query_params.movie_tracks_parse import MovieTracksParse
from src.query_params.top_players_query import TopPlayersQuery
from src.utils.auth import get_user
from src.utils.common import get_static_hash, get_word_form

router = APIRouter()


@router.get("/")
def index(user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    top_players = quiz_tours_database.get_top_players(query={})

    template = templates.get_template("index.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        top_players=top_players,
        get_word_form=get_word_form
    )

    return HTMLResponse(content=content)


@router.post("/parse-movies")
def parse_movies(params: MovieParse, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if user.role == UserRole.USER:
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    try:
        movies = kinopoisk_parser.parse_movies(movie_ids=params.movie_ids, max_images=params.max_images)
        new_movies, new_persons = movie_database.add_from_kinopoisk(movies=movies, username=user.username)
        removed_persons = movie_database.remove_empty_persons(username="dronperminov")
        return JSONResponse({"status": "success", "movies": len(movies), "new_movies": new_movies, "new_persons": new_persons, "removed_persons": removed_persons})
    except Exception as error:
        return JSONResponse({"status": "error", "message": str(error)})


@router.post("/parse-movie-tracks")
def parse_movie_tracks(params: MovieTracksParse, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if user.role == UserRole.USER:
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    try:
        tracks = yandex_music_parser.parse_tracks(track_ids=params.track_ids)
        movie_database.add_tracks_from_yandex(movie_id=params.movie_id, tracks=tracks)
        return JSONResponse({"status": "success", "tracks": len(tracks)})
    except Exception as error:
        return JSONResponse({"status": "error", "message": str(error)})


@router.post("/history")
def get_history(params: HistoryQuery) -> JSONResponse:
    query = {"name": {"$in": params.actions}}
    history = list(database.history.find(query, {"_id": 0}).sort("timestamp", -1).skip(params.skip).limit(params.limit))
    return JSONResponse({"status": "success", "history": jsonable_encoder(history)})


@router.post("/get-top-players")
def get_top_players(params: TopPlayersQuery) -> JSONResponse:
    players = quiz_tours_database.get_top_players(params.to_query())
    return JSONResponse({"status": "success", "players": jsonable_encoder(players)})


@router.post("/get-direct-link")
def get_direct_link(params: DirectLink) -> JSONResponse:
    direct_link = yandex_music_parser.get_track_link(params.yandex_id)

    if not direct_link:
        return JSONResponse({"status": "error", "message": "Не удалось получить ссылку на аудио"})

    return JSONResponse({"status": "success", "direct_link": direct_link})
