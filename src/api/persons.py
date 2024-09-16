from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from src import movie_database
from src.api import send_error, templates
from src.entities.user import User
from src.query_params.person_movies import PersonMovies
from src.utils.auth import get_user
from src.utils.common import get_static_hash

router = APIRouter()


@router.get("/persons/{person_id}")
def get_person(person_id: int, user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    person = movie_database.get_person(person_id=person_id)

    if person is None:
        return send_error(title="Персона не найдена", text="Не удалось найти запрашиваемую персону. Возможно, она была удалена", user=user)

    template = templates.get_template("persons/person.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        person=person
    )
    return HTMLResponse(content=content)


@router.post("/person-movies")
def get_person_movies(params: PersonMovies) -> JSONResponse:
    total, movies = movie_database.get_person_movies(params=params)
    person_id2person = movie_database.get_movies_persons(movies=movies)

    return JSONResponse({
        "status": "success",
        "total": total,
        "movies": jsonable_encoder(movies),
        "person_id2person": jsonable_encoder(person_id2person)
    })
