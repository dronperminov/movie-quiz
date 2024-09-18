import logging
import random
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np

from src.database import Database
from src.entities.movie import Movie
from src.entities.question import MovieByActorsQuestion, MovieByCharactersQuestion, MovieByDescriptionQuestion, MovieByImageQuestion, MovieBySloganQuestion, Question
from src.entities.question_answer import QuestionAnswer
from src.entities.question_settings import QuestionSettings
from src.entities.settings import Settings
from src.entities.user import User
from src.enums import QuestionType
from src.movie_database import MovieDatabase


class QuestionsDatabase:
    def __init__(self, database: Database, movie_database: MovieDatabase, logger: logging.Logger) -> None:
        self.database = database
        self.movie_database = movie_database
        self.logger = logger

        self.alpha = 0.999
        self.last_questions_count = 500
        self.min_incorrect_count = 20

    def have_question(self, username: str) -> bool:
        return self.__get_user_question(username=username) is not None

    def answer_question(self, username: str, answer: QuestionAnswer) -> None:
        question = self.__get_user_question(username=username)
        question.set_answer(answer)
        self.database.questions.update_one({"username": username, "correct": None}, {"$set": question.to_dict()})

    def get_question(self, settings: Settings, external_questions: Optional[List[Question]] = None) -> Optional[Question]:
        movies = self.get_question_movies(settings.question_settings)

        if not movies:
            return None

        if external_questions is None and (question := self.__get_user_question(username=settings.username)):
            if question.is_valid({movie["movie_id"] for movie in movies}, settings.question_settings):
                return self.update_question(question, settings.question_settings)

            self.database.questions.delete_one({"username": settings.username, "correct": None})

        if external_questions:
            last_questions = external_questions
        else:
            last_questions = self.__get_last_questions(username=settings.username, movie_ids=[movie["movie_id"] for movie in movies])

        last_incorrect_questions = [question for question in last_questions if not question.correct and question.question_type in settings.question_settings.question_types]

        if len(last_incorrect_questions) >= self.min_incorrect_count and random.random() < settings.question_settings.repeat_incorrect_probability:
            question = self.repeat_incorrect_question(last_incorrect_questions, settings.question_settings)
        else:
            movie = self.sample_question_movies(movies=movies, last_questions=last_questions, settings=settings.question_settings, count=1)[0]
            question = self.generate_question(movie=movie, username=settings.username, settings=settings.question_settings)

        if external_questions is None:
            self.database.questions.insert_one(question.to_dict())

        return question

    def generate_question(self, movie: Movie, username: str, settings: QuestionSettings) -> Question:
        question_types = list(set(settings.question_types).intersection(movie.get_question_types()))
        question_weights = [settings.question_types[question_type] for question_type in question_types]
        question_type = random.choices(question_types, weights=question_weights, k=1)[0]
        return self.__generate_question_by_type(question_type=question_type, movie=movie, username=username, settings=settings)

    def repeat_incorrect_question(self, last_incorrect_questions: List[Question], settings: QuestionSettings) -> Question:
        question_weights = [1 - self.alpha ** (i + 1) for i in range(len(last_incorrect_questions))]
        question = random.choices(last_incorrect_questions, weights=question_weights, k=1)[0]
        question.remove_answer()
        return self.update_question(question, settings)

    def sample_question_movies(self, movies: List[dict], last_questions: List[Question], settings: QuestionSettings, count: int) -> List[Movie]:
        movie_id2weight = dict()

        for i, question in enumerate(last_questions):
            if question.movie_id not in movie_id2weight:
                movie_id2weight[question.movie_id] = 1 - self.alpha ** (i + 1)

        feature2balance = {
            "movie_type": {movie_type.value: value for movie_type, value in settings.movie_types.items()},
            "production": {production.value: value for production, value in settings.production.items()},
            "year": {years: value for years, value in settings.years.items()}
        }

        year2key = settings.get_possible_years()
        features2count = defaultdict(int)

        for movie in movies:
            movie["year"] = year2key[movie["year"]]
            movie["production"] = movie["production"][0]
            features2count[tuple(movie[feature] for feature in feature2balance)] += 1

        movie_weights = [self.__get_movie_weight(movie, feature2balance, features2count, movie_id2weight) for movie in movies]

        total_weight = sum(movie_weights)
        movie_weights = [weight / total_weight for weight in movie_weights]
        movies = np.random.choice(movies, p=movie_weights, replace=False, size=count)
        return self.movie_database.get_movies(movie_ids=[movie["movie_id"] for movie in movies])

    def get_question_movies(self, settings: QuestionSettings) -> List[dict]:
        return list(self.database.movies.find(settings.to_query(), {"movie_id": 1, "movie_type": 1, "production": 1, "year": 1}))

    def get_movies_scales(self, user: Optional[User], movies: List[Movie]) -> Dict[int, dict]:
        if not user:
            return {}

        settings = self.database.get_settings(username=user.username)
        if not settings.show_knowledge_status:
            return {}

        movie_ids = list({movie.movie_id for movie in movies})
        questions = list(self.database.questions.find({"username": user.username, "correct": {"$ne": None}, "movie_id": {"$in": movie_ids}}))
        movie_id2scale = {question["movie_id"]: {"incorrect": 0, "correct": 0, "scale": 0} for question in questions}

        for question in questions:
            movie_id2scale[question["movie_id"]]["correct" if question["correct"] else "incorrect"] += 1

        for movie_id, scales in movie_id2scale.items():
            movie_id2scale[movie_id]["scale"] = scales["correct"] / (scales["correct"] + scales["incorrect"])

        return movie_id2scale

    def update_question(self, question: Question, settings: QuestionSettings) -> Question:
        movie = self.movie_database.get_movie(movie_id=question.movie_id)
        person_id2person = self.movie_database.get_movies_persons(movies=[movie])
        return question.update(movie=movie, person_id2person=person_id2person, settings=settings)

    def __get_movie_weight(self, movie: dict, feature2balance: Dict[str, Dict[str, float]], features2count: Dict[tuple, float], movie_id2weight: Dict[int, float]) -> float:
        movie_weight = 1 / features2count[tuple(movie[feature] for feature in feature2balance)]

        for feature, feature2value in feature2balance.items():
            movie_weight *= feature2value[movie[feature]]

        return movie_weight * movie_id2weight.get(movie["movie_id"], 1)

    def __generate_question_by_type(self, question_type: QuestionType, movie: Movie, username: str, settings: QuestionSettings) -> Question:
        person_id2person = self.movie_database.get_movies_persons(movies=[movie])

        if question_type == QuestionType.MOVIE_BY_SLOGAN:
            return MovieBySloganQuestion.generate(movie=movie, username=username)

        if question_type in [QuestionType.MOVIE_BY_SHORT_DESCRIPTION, QuestionType.MOVIE_BY_DESCRIPTION]:
            return MovieByDescriptionQuestion.generate(movie=movie, username=username, question_type=question_type)

        if question_type == QuestionType.MOVIE_BY_IMAGE:
            return MovieByImageQuestion.generate(movie=movie, username=username)

        if question_type == QuestionType.MOVIE_BY_ACTORS:
            return MovieByActorsQuestion.generate(movie=movie, username=username, person_id2person=person_id2person, hide_actor_photos=settings.hide_actor_photos)

        if question_type == QuestionType.MOVIE_BY_CHARACTERS:
            return MovieByCharactersQuestion.generate(movie=movie, username=username)

        raise ValueError("Invalid question type")

    def __get_user_question(self, username: str) -> Optional[Question]:
        question = self.database.questions.find_one({"username": username, "correct": None})
        return Question.from_dict(question) if question else None

    def __get_last_questions(self, username: str, movie_ids: List[int]) -> List[Question]:
        query = {"username": username, "correct": {"$ne": None}, "movie_id": {"$in": movie_ids}}
        last_questions = self.database.questions.find(query).sort("timestamp", -1).limit(self.last_questions_count)
        return [Question.from_dict(question) for question in last_questions]
