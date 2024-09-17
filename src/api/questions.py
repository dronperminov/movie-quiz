from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response

from src import database, movie_database, questions_database
from src.api import login_redirect, send_error, templates
from src.entities.question_answer import QuestionAnswer
from src.entities.user import User
from src.utils.auth import get_user
from src.utils.common import get_static_hash

router = APIRouter()


@router.get("/question")
def get_question(user: Optional[User] = Depends(get_user)) -> Response:
    if not user:
        return login_redirect(back_url="/question")

    settings = database.get_settings(username=user.username)
    question = questions_database.get_question(settings)

    if question is None:
        return send_error(user=user, title="Не удалось сгенерировать вопрос", text='Нет КМС, удовлетворяющих выбранным <a class="link" href="/settings">настройкам</a>.')

    movie = movie_database.get_movie(movie_id=question.movie_id)
    person_id2person = movie_database.get_movies_persons(movies=[movie])

    template = templates.get_template("user/question.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        question=jsonable_encoder(question),
        movie=jsonable_encoder(movie),
        person_id2person=jsonable_encoder(person_id2person)
    )
    return HTMLResponse(content=content)


@router.post("/question")
def post_question(user: Optional[User] = Depends(get_user)) -> JSONResponse:
    settings = database.get_settings(username=user.username)
    question = questions_database.get_question(settings)

    if question is None:
        return JSONResponse({"status": "error", "message": "Нет КМС, удовлетворяющих выбранным настройкам."})

    movie = movie_database.get_movie(movie_id=question.movie_id)
    person_id2person = movie_database.get_movies_persons(movies=[movie])
    return JSONResponse({
        "status": "success",
        "question": jsonable_encoder(question),
        "movie": jsonable_encoder(movie),
        "person_id2person": jsonable_encoder(person_id2person)
    })


@router.post("/answer-question")
def answer_question(answer: QuestionAnswer, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if not questions_database.have_question(user.username):
        return JSONResponse({"status": "error", "message": "В базе отсутствует вопрос, на который можно ответить"})

    questions_database.answer_question(user.username, answer)
    return JSONResponse({"status": "success"})
