from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response

from src import database
from src.api import login_redirect, templates
from src.entities.main_settings import MainSettings
from src.entities.question_settings import QUESTION_YEARS, QuestionSettings
from src.entities.user import User
from src.enums import MovieType, Production, QuestionType
from src.utils.auth import get_user
from src.utils.common import get_static_hash

router = APIRouter()


@router.get("/settings")
def get_settings(user: Optional[User] = Depends(get_user)) -> Response:
    if not user:
        return login_redirect(back_url="/settings")

    settings = database.get_settings(username=user.username)
    template = templates.get_template("user/settings.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        settings=settings,
        MovieType=MovieType,
        Production=Production,
        QuestionType=QuestionType,
        today=datetime.today(),
        question_years=QUESTION_YEARS
    )
    return HTMLResponse(content=content)


@router.post("/main_settings")
def update_main_settings(main_settings: MainSettings, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    settings = database.get_settings(username=user.username)
    database.update_settings(settings.update_main(main_settings))
    return JSONResponse({"status": "success"})


@router.post("/question_settings")
def update_question_settings(question_settings: QuestionSettings, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    settings = database.get_settings(username=user.username)
    database.update_settings(settings.update_question(question_settings))
    return JSONResponse({"status": "success"})
