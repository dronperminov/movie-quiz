from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import database, movie_database, questions_database, quiz_tours_database
from src.api import login_redirect, send_error, templates
from src.entities.quiz_tour import QuizTour
from src.entities.quiz_tour_question_answer import QuizTourQuestionAnswer
from src.entities.user import User
from src.enums import QuizTourType
from src.query_params.quiz_tours_search import QuizToursSearch, QuizToursSearchQuery
from src.utils.auth import get_user
from src.utils.common import format_time, get_static_hash

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


@router.get("/quiz-tours/{quiz_tour_id}")
def get_quiz_tour_question(quiz_tour_id: int, user: Optional[User] = Depends(get_user)) -> Response:
    if not user:
        return login_redirect(back_url=f"/quiz-tours/{quiz_tour_id}")

    quiz_tour = quiz_tours_database.get_quiz_tour(quiz_tour_id=quiz_tour_id)

    if not quiz_tour:
        return send_error(user=user, title="Запрашиваемый квиз не существует", text="Не удалось найти запрашиваемый квиз. Возможно, он был удалён или ещё не был создан.")

    quiz_tour_question = quiz_tours_database.get_quiz_tour_question(username=user.username, quiz_tour=quiz_tour)

    if quiz_tour_question is None:
        return RedirectResponse(f"/quiz-tour/{quiz_tour_id}")

    question = quiz_tour_question.question

    movie = movie_database.get_movie(movie_id=question.movie_id)
    person_id2person = movie_database.get_movies_persons(movies=[movie])
    movie_id2scale = questions_database.get_movies_scales(user=user, movies=[movie])

    template = templates.get_template("user/question.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        question_id=quiz_tour_question.question_id,
        question=jsonable_encoder(question),
        questions_count=len(quiz_tour.question_ids),
        question_number=quiz_tour.question_ids.index(quiz_tour_question.question_id) + 1,
        movie=jsonable_encoder(movie),
        person_id2person=jsonable_encoder(person_id2person),
        movie_id2scale=jsonable_encoder(movie_id2scale)
    )
    return HTMLResponse(content=content)


@router.get("/quiz-tour/{quiz_tour_id}")
def get_quiz_tour(quiz_tour_id: int, user: Optional[User] = Depends(get_user)) -> Response:
    if not user:
        return login_redirect(back_url=f"/quiz-tours/{quiz_tour_id}")

    quiz_tour = quiz_tours_database.get_quiz_tour(quiz_tour_id=quiz_tour_id)

    if not quiz_tour:
        return send_error(user=user, title="Запрашиваемый квиз не существует", text="Не удалось найти запрашиваемый квиз. Возможно, он был удалён или ещё не был создан.")

    if not quiz_tours_database.is_tour_ended(username=user.username, quiz_tour=quiz_tour):
        return RedirectResponse(f"/quiz-tours/{quiz_tour_id}")

    statuses = quiz_tours_database.get_quiz_tours_statuses(username=user.username, quiz_tours=[quiz_tour])
    movie_id2status = quiz_tours_database.get_quiz_tour_movies_statuses(quiz_tour=quiz_tour)
    movie_id2correct = quiz_tours_database.get_quiz_tour_movie_results(username=user.username, quiz_tour=quiz_tour)
    movies = movie_database.get_movies(list(movie_id2correct))
    person_id2person = movie_database.get_movies_persons(movies=movies)
    movie_id2scale = questions_database.get_movies_scales(user=user, movies=movies)

    template = templates.get_template("quiz_tours/quiz_tour.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        quiz_tour=jsonable_encoder(quiz_tour),
        statuses=statuses,
        movie_id2correct=jsonable_encoder(movie_id2correct),
        movie_id2status=jsonable_encoder(movie_id2status),
        movies=jsonable_encoder(movies),
        person_id2person=jsonable_encoder(person_id2person),
        movie_id2scale=jsonable_encoder(movie_id2scale),
        format_time=format_time
    )
    return HTMLResponse(content=content)


@router.post("/answer-quiz-tour-question")
def answer_quiz_tour_question(answer: QuizTourQuestionAnswer, user: Optional[User] = Depends(get_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не авторизован"})

    if not quiz_tours_database.have_question(username=user.username, question_id=answer.question_id):
        return JSONResponse({"status": "error", "message": "В базе отсутствует вопрос, на который можно ответить"})

    quiz_tours_database.answer_question(user.username, answer)
    quiz_tour = database.quiz_tours.find_one({"question_ids": answer.question_id})

    if not quiz_tour:
        return JSONResponse({"status": "error", "message": "Не удалось найти запрашиваемый квиз. Возможно, он был удалён или ещё не был создан."})

    quiz_tour = QuizTour.from_dict(quiz_tour)
    quiz_tour_question = quiz_tours_database.get_quiz_tour_question(username=user.username, quiz_tour=quiz_tour)

    if quiz_tour_question is None:
        return JSONResponse({"status": "success", "redirect": f"/quiz-tour/{quiz_tour.quiz_tour_id}"})

    question = quiz_tour_question.question

    movie = movie_database.get_movie(movie_id=question.movie_id)
    person_id2person = movie_database.get_movies_persons(movies=[movie])
    movie_id2scale = questions_database.get_movies_scales(user=user, movies=[movie])

    return JSONResponse({
        "status": "success",
        "question_id": quiz_tour_question.question_id,
        "question": jsonable_encoder(question),
        "movie": jsonable_encoder(movie),
        "person_id2person": jsonable_encoder(person_id2person),
        "movie_id2scale": jsonable_encoder(movie_id2scale)
    })
