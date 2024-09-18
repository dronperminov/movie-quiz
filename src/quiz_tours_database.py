import logging
import re
from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from rapidfuzz import fuzz

from src import Database, QuestionsDatabase
from src.entities.movie import Movie
from src.entities.question import Question
from src.entities.question_settings import QuestionSettings
from src.entities.quiz_tour import QuizTour
from src.entities.quiz_tour_answer import QuizTourAnswer
from src.entities.quiz_tour_question import QuizTourQuestion
from src.entities.quiz_tour_question_answer import QuizTourQuestionAnswer
from src.entities.user import User
from src.enums import QuizTourType
from src.query_params.quiz_tours_search import QuizToursSearch


class QuizToursDatabase:
    def __init__(self, database: Database, questions_database: QuestionsDatabase, logger: logging.Logger) -> None:
        self.database = database
        self.questions_database = questions_database
        self.logger = logger

        self.last_questions_count = 1000
        self.rating_alpha = 0.99
        self.rating_min_quiz_tours_count = 4

        # eng to rus
        self.pair_letters = {
            "A": "A", "B": "Б", "V": "В", "G": "Г", "D": "Д", "E": "Е", "J": "Ж", "Z": "З", "I": "И", "K": "К",
            "L": "Л", "M": "М", "N": "Н", "O": "О", "P": "П", "R": "Р", "S": "С", "T": "Т", "U": "У", "F": "Ф", "H": "Х"
        }

    def get_rating(self, username: str, query: dict) -> Optional[Tuple[float, int]]:
        answers = self.database.quiz_tour_answers.find({"username": username})
        question_id2correct = {answer["question_id"]: answer["correct"] for answer in answers}
        corrects = []

        quiz_tour_id2date = {quiz_tour["quiz_tour_id"]: quiz_tour["created_at"].date() for quiz_tour in self.database.quiz_tours.find(query).sort("created_at", -1)}
        max_date = max(quiz_tour_id2date.values(), default=date.today())
        quiz_tour_id2scale = {quiz_tour_id: self.rating_alpha ** (max_date - quiz_tour_date).days for quiz_tour_id, quiz_tour_date in quiz_tour_id2date.items()}

        for quiz_tour in self.database.quiz_tours.find({"question_ids": {"$in": list(question_id2correct)}}):
            if quiz_tour["quiz_tour_id"] not in quiz_tour_id2date:
                continue

            question_ids = quiz_tour["question_ids"]
            scores = [question_id2correct[question_id] for question_id in question_ids if question_id in question_id2correct]

            if len(scores) == len(question_ids):
                corrects.append(sum(scores) / len(question_ids) * 100 * quiz_tour_id2scale[quiz_tour["quiz_tour_id"]])

        return (round(sum(corrects) / len(corrects), 1), len(corrects)) if corrects else None

    def get_top_players(self, query: dict) -> List[Tuple[User, float, int]]:
        available_usernames = [settings["username"] for settings in self.database.settings.find({"show_progress": True}, {"username": 1})]
        username2user = {user.username: user for user in self.database.get_users(usernames=available_usernames)}
        username2rating = defaultdict(int)

        for username in available_usernames:
            rating = self.get_rating(username=username, query=query)

            if rating is not None and rating[1] >= self.rating_min_quiz_tours_count:
                username2rating[username] = rating

        top_players = sorted([(rating, count, username) for username, (rating, count) in username2rating.items()], reverse=True)
        return [(username2user[username], rating, count) for rating, count, username in top_players]

    def get_quiz_tours(self, username: Optional[str], params: QuizToursSearch) -> Tuple[int, List[QuizTour]]:
        query = params.to_query()
        quiz_tours = [QuizTour.from_dict(quiz_tour) for quiz_tour in self.database.quiz_tours.find(query)]
        finished_quiz_tour_ids = set()

        if username is not None:
            filtered_quiz_tours = []
            for quiz_tour in quiz_tours:
                answers = self.database.quiz_tour_answers.count_documents({"username": username, "question_id": {"$in": quiz_tour.question_ids}})

                if not params.check_complete(answers, len(quiz_tour.question_ids)):
                    continue

                filtered_quiz_tours.append(quiz_tour)

                if answers == len(quiz_tour.question_ids):
                    finished_quiz_tour_ids.add(quiz_tour.quiz_tour_id)

            quiz_tours = filtered_quiz_tours

        quiz_tours = sorted(quiz_tours, key=lambda quiz_tour: (quiz_tour.quiz_tour_id not in finished_quiz_tour_ids, quiz_tour.quiz_tour_id), reverse=True)
        skip = params.page * params.page_size
        return len(quiz_tours), quiz_tours[skip:skip + params.page_size]

    def get_quiz_tour(self, quiz_tour_id: int) -> Optional[QuizTour]:
        quiz_tour = self.database.quiz_tours.find_one({"quiz_tour_id": quiz_tour_id})
        return QuizTour.from_dict(quiz_tour) if quiz_tour else None

    def get_quiz_tour_movie_results(self, username: str, quiz_tour: QuizTour) -> Dict[int, bool]:
        questions = self.database.quiz_tour_questions.find({"question_id": {"$in": quiz_tour.question_ids}}, {"question.movie_id": 1, "question_id": 1})
        answers = self.database.quiz_tour_answers.find({"username": username, "question_id": {"$in": quiz_tour.question_ids}})
        question_id2answer = {answer["question_id"]: answer["correct"] for answer in answers}
        return {question["question"]["movie_id"]: question_id2answer[question["question_id"]] for question in questions}

    def is_tour_ended(self, username: str, quiz_tour: QuizTour) -> bool:
        return self.database.quiz_tour_answers.count_documents({"username": username, "question_id": {"$in": quiz_tour.question_ids}}) == len(quiz_tour.question_ids)

    def get_quiz_tour_question(self, username: str, quiz_tour: QuizTour) -> Optional[QuizTourQuestion]:
        answers = list(self.database.quiz_tour_answers.find({"username": username, "question_id": {"$in": quiz_tour.question_ids}}).sort("question_id", -1))

        if len(answers) == len(quiz_tour.question_ids):
            return None

        question = QuizTourQuestion.from_dict(self.database.quiz_tour_questions.find_one({"question_id": quiz_tour.question_ids[len(answers)]}))
        question.question = self.questions_database.update_question(question.question, QuestionSettings.default())
        question.question.title = f"Вопрос {quiz_tour.question_ids.index(question.question_id) + 1} из {len(quiz_tour.question_ids)}. {question.question.title}"
        return question

    def have_question(self, question_id: int, username: str) -> bool:
        if self.database.quiz_tour_questions.find_one({"question_id": question_id}, {"question_id": 1}) is None:
            return False

        if self.database.quiz_tour_answers.find_one({"question_id": question_id, "username": username}) is not None:
            return False

        return True

    def answer_question(self, username: str, answer: QuizTourQuestionAnswer) -> None:
        answer = QuizTourAnswer(question_id=answer.question_id, username=username, correct=answer.correct, timestamp=datetime.now(), answer_time=answer.answer_time)
        self.database.quiz_tour_answers.insert_one(answer.to_dict())

    def get_quiz_tours_statuses(self, username: str, quiz_tours: List[QuizTour]) -> Dict[int, dict]:
        return {quiz_tour.quiz_tour_id: self.__get_quiz_tour_status(quiz_tour=quiz_tour, username=username) for quiz_tour in quiz_tours}

    def get_quiz_tour_movies_statuses(self, quiz_tour: QuizTour) -> Dict[int, list]:
        movie_id2answers = defaultdict(list)
        questions = self.database.quiz_tour_questions.find({"question_id": {"$in": quiz_tour.question_ids}}, {"question.movie_id": 1, "question_id": 1})
        question_id2movie_id = {question["question_id"]: question["question"]["movie_id"] for question in questions}

        for answer in self.database.quiz_tour_answers.find({"question_id": {"$in": quiz_tour.question_ids}}):
            movie_id2answers[question_id2movie_id[answer["question_id"]]].append(answer["correct"])
        return movie_id2answers

    def generate_tour(self, params: dict, quiz_tour_type: QuizTourType, settings: QuestionSettings, questions_count: int) -> Optional[QuizTour]:
        movies = self.questions_database.get_question_movies(settings)

        if len(movies) < questions_count:
            return None

        last_questions = self.__get_last_questions(movie_ids=[movie["movie_id"] for movie in movies])

        if quiz_tour_type == QuizTourType.REGULAR:
            questions = self.__generate_regular_tour_questions(movies=movies, last_questions=last_questions, settings=settings, count=questions_count)
        else:
            raise ValueError(f'Invalid quiz tour type "{quiz_tour_type}"')

        quiz_tour_questions = self.__convert_to_quiz_tour_questions(questions=questions)
        quiz_tour = QuizTour(
            quiz_tour_id=self.database.get_identifier("quiz_tours"),
            quiz_tour_type=quiz_tour_type,
            name=params["name"],
            description=params["description"],
            question_ids=[question.question_id for question in quiz_tour_questions],
            image_url=params.get("image_url", "/images/quiz_tours/default.png"),
            created_at=datetime.now(),
            created_by="system",
            tags=params.get("tags", [])
        )

        self.database.quiz_tours.insert_one(quiz_tour.to_dict())
        return quiz_tour

    def __generate_regular_tour_questions(self, movies: List[dict], last_questions: List[Question], settings: QuestionSettings, count: int) -> List[Question]:
        questions = []
        sampled_names = []

        for _ in range(count):
            movie = self.questions_database.sample_question_movies(movies=movies, last_questions=last_questions, settings=settings, count=1)[0]
            question = self.questions_database.generate_question(movie=movie, username="", settings=settings)
            questions.append(question)
            last_questions.append(question)
            movies = self.__exclude_similar_movies(sampled_names=sampled_names, sampled_movie=movie, movies=movies)

        return questions

    def __exclude_similar_movies(self, sampled_names: List[str], sampled_movie: Movie, movies: List[dict]) -> List[dict]:
        sampled_names.append(self.__preprocess_name(sampled_movie.name))
        return [movie for movie in movies if not self.__is_similar_movie(movie["name"], sampled_names)]

    def __preprocess_name(self, name: str) -> str:
        return re.sub(r"\W+", " ", name)

    def __is_similar_movie(self, name: str, names: List[str]) -> bool:
        name_words = self.__preprocess_name(name).split(" ")

        for sampled_name in names:
            words = sampled_name.split(" ")
            length = min(3, max(len(name_words), len(words)))
            if fuzz.partial_ratio(" ".join(name_words[:length]), " ".join(words[:length])) > 80:
                return True

        return False

    def __get_last_questions(self, movie_ids: List[int]) -> List[Question]:
        last_questions = self.database.quiz_tour_questions.find({"question.movie_id": {"$in": movie_ids}}).sort("question_id", -1).limit(self.last_questions_count)
        return [Question.from_dict(question["question"]) for question in last_questions]

    def __convert_to_quiz_tour_questions(self, questions: List[Question], answer_time: float = 45) -> List[QuizTourQuestion]:
        quiz_tour_questions = []

        for question in questions:
            question_id = self.database.get_identifier("quiz_tour_questions")
            tour_question = QuizTourQuestion(question_id=question_id, question=question, answer_time=answer_time)

            self.database.quiz_tour_questions.insert_one(tour_question.to_dict())
            quiz_tour_questions.append(tour_question)

        return quiz_tour_questions

    def __get_quiz_tour_status(self, quiz_tour: QuizTour, username: str) -> dict:
        status = {True: 0, False: 0}
        time = {True: 0, False: 0}

        username2count = defaultdict(list)

        for answer in self.database.quiz_tour_answers.find({"question_id": {"$in": quiz_tour.question_ids}}):
            username2count[answer["username"]].append(answer["correct"])

            if answer["username"] == username:
                status[answer["correct"]] += 1
                time[answer["correct"]] += answer["answer_time"]

        username2score = {username: sum(answers) / len(answers) for username, answers in username2count.items() if len(answers) == len(quiz_tour.question_ids)}

        return {
            "correct": status[True],
            "incorrect": status[False],
            "lost": len(quiz_tour.question_ids) - sum(status.values()),
            "total": len(quiz_tour.question_ids),
            "correct_percents": status[True] / len(quiz_tour.question_ids) * 100,
            "incorrect_percents": status[False] / len(quiz_tour.question_ids) * 100,
            "time": {
                "correct": time[True],
                "incorrect": time[False],
                "total": time[True] + time[False]
            },
            "finished_count": len(username2score),
            "mean_score": sum(username2score.values()) / max(len(username2score), 1) * 100
        }
