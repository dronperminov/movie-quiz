from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from src import quiz_tours_database
from src.api import templates
from src.entities.quiz_tour_question_answer import QuizTourQuestionAnswer
from src.entities.user import User
from src.enums import QuizTourType
from src.query_params.quiz_tours_search import QuizToursSearch, QuizToursSearchQuery
from src.utils.auth import get_user
from src.utils.common import get_static_hash

router = APIRouter()


@router.get("/quiz-tours")
def get_quiz_tours(params: QuizToursSearchQuery = Depends(), user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    template = templates.get_template("quiz_tours/quiz_tours.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        search_params=params.to_params(user is not None),
        QuizTourType=QuizTourType
    )
    return HTMLResponse(content=content)


@router.post("/quiz-tours")
def search_quiz_tours(params: QuizToursSearch, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    total, quiz_tours = quiz_tours_database.get_quiz_tours(username=user.username if user else None, params=params)
    quiz_tour_id2statuses = quiz_tours_database.get_quiz_tours_statuses(username=user.username, quiz_tours=quiz_tours) if user else {}
    return JSONResponse({"status": "success", "total": total, "quiz_tours": jsonable_encoder(quiz_tours), "statuses": quiz_tour_id2statuses})


@router.post("/answer-quiz-tour-question")
def answer_quiz_tour_question(answer: QuizTourQuestionAnswer, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if not quiz_tours_database.have_question(username=user.username, question_id=answer.question_id):
        return JSONResponse({"status": "error", "message": "В базе отсутствует вопрос, на который можно ответить"})

    quiz_tours_database.answer_question(user.username, answer)
    return JSONResponse({"status": "success"})
