from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from src import movie_database
from src.api import send_error, templates
from src.entities.user import User
from src.enums import MovieType, Production
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
        search_params=search_params
    )

    return HTMLResponse(content=content)


@router.post("/movies")
def search_movies(params: MovieSearch) -> JSONResponse:
    total, movies = movie_database.search_movies(params=params)
    person_id2person = movie_database.get_movies_persons(movies=movies)

    return JSONResponse({
        "status": "success",
        "total": total,
        "movies": jsonable_encoder(movies),
        "person_id2person": jsonable_encoder(person_id2person)
    })


@router.get("/movies/{movie_id}")
def get_movie(movie_id: int, user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    movie = movie_database.get_movie(movie_id=movie_id)

    if movie is None:
        return send_error(title="Фильм не найден", text="Не удалось найти запрашиваемый фильм. Возможно, он был удалён", user=user)

    person_id2person = movie_database.get_movies_persons(movies=[movie])

    template = templates.get_template("movies/movie.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        movie=movie,
        person_id2person=person_id2person,
        jsonable_encoder=jsonable_encoder,
        get_word_form=get_word_form
    )
    return HTMLResponse(content=content)
