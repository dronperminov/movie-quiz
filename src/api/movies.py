import random
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from src import database, movie_database, questions_database
from src.api import send_error, templates
from src.entities.question_settings import QuestionSettings
from src.entities.user import User
from src.enums import Genre, MovieType, Production, UserRole
from src.query_params.movie_remove import MovieRemove
from src.query_params.movie_search import MovieSearch
from src.query_params.movie_search_query import MovieSearchQuery
from src.utils.auth import get_user
from src.utils.common import get_static_hash, get_word_form

router = APIRouter()


@router.get("/movies")
def get_movies(user: Optional[User] = Depends(get_user), params: MovieSearchQuery = Depends()) -> HTMLResponse:
    search_params = params.to_search_params()
    last_added_movies = movie_database.get_last_movies(order_field="metadata.created_at", order_type=-1, count=10)
    last_updated_movies = movie_database.get_last_movies(order_field="metadata.updated_at", order_type=-1, count=10)
    top_voted_movies = movie_database.get_last_movies(order_field="rating.votes_kp", order_type=-1, count=10)

    template = templates.get_template("movies/movies.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        movies_count=movie_database.get_movies_count(),
        get_word_form=get_word_form,
        last_added_movies=last_added_movies,
        last_updated_movies=last_updated_movies,
        top_voted_movies=top_voted_movies,
        MovieType=MovieType,
        Production=Production,
        Genre=Genre,
        search_params=search_params
    )

    return HTMLResponse(content=content)


@router.post("/movies")
def search_movies(params: MovieSearch, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    total, movies = movie_database.search_movies(params=params)
    person_id2person = movie_database.get_movies_persons(movies=movies)
    movie_id2scale = questions_database.get_movies_scales(user=user, movies=movies)

    return JSONResponse({
        "status": "success",
        "total": total,
        "movies": jsonable_encoder(movies),
        "person_id2person": jsonable_encoder(person_id2person),
        "movie_id2scale": jsonable_encoder(movie_id2scale)
    })


def get_movie_response(movie_id: int, user: Optional[User]) -> HTMLResponse:
    movie = movie_database.get_movie(movie_id=movie_id)

    if movie is None:
        return send_error(title="Фильм не найден", text="Не удалось найти запрашиваемый фильм. Возможно, он был удалён", user=user)

    sequels = movie_database.get_movies(movie_ids=movie.sequels)
    person_id2person = movie_database.get_movies_persons(movies=[movie, *sequels])
    movie_id2cites = movie_database.get_movies_cites(movies=[movie])
    movie_id2tracks = movie_database.get_movies_tracks(movies=[movie])
    movie_id2scale = questions_database.get_movies_scales(user=user, movies=[movie, *sequels])

    template = templates.get_template("movies/movie.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        movie=jsonable_encoder(movie),
        person_id2person=jsonable_encoder(person_id2person),
        cites=jsonable_encoder(movie_id2cites[movie.movie_id]),
        tracks=jsonable_encoder(movie_id2tracks[movie.movie_id]),
        movie_id2scale=jsonable_encoder(movie_id2scale),
        sequels=jsonable_encoder(sequels)
    )
    return HTMLResponse(content=content)


@router.get("/movies/random")
def get_random_movie(user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    settings = database.get_settings(username=user.username).question_settings if user else QuestionSettings.default()
    movies = questions_database.get_question_movies(settings=settings)

    if not movies:
        movies = questions_database.get_question_movies(settings=QuestionSettings.default())

    movie_id = random.choice([movie["movie_id"] for movie in movies])
    return get_movie_response(movie_id=movie_id, user=user)


@router.get("/movies/{movie_id}")
def get_movie(movie_id: int, user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    return get_movie_response(movie_id=movie_id, user=user)


@router.post("/remove-movie")
def remove_movie(params: MovieRemove, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if user.role != UserRole.OWNER:
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    movie = movie_database.get_movie(movie_id=params.movie_id)
    if movie is None:
        return JSONResponse({"status": "error", "message": f"Не удалось найти фильм с movie_id = {params.movie_id} в базе"})

    movie_database.remove_movie(movie_id=params.movie_id, username=user.username)
    return JSONResponse({"status": "success"})


@router.get("/movie-history/{movie_id}")
def get_movie_history(movie_id: int) -> JSONResponse:
    history = list(database.history.find({"movie_id": movie_id}, {"_id": 0}).sort("timestamp", -1))
    return JSONResponse({"status": "success", "history": jsonable_encoder(history)})
