import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from typing_extensions import Self

from src.entities.movie import Movie
from src.entities.person import Person
from src.entities.question_answer import QuestionAnswer
from src.entities.question_settings import QuestionSettings
from src.entities.spoiler_text import SpoilerText
from src.enums import QuestionType


@dataclass
class Question:
    question_type: QuestionType = field(init=False)
    username: str = field(init=False)
    movie_id: int = field(init=False)
    title: str
    answer: str
    correct: Optional[bool] = field(init=False)
    answer_time: Optional[float] = field(init=False)
    timestamp: datetime = field(init=False)

    def init_base(self, question_type: QuestionType, username: str, movie_id: int) -> None:
        self.question_type = question_type
        self.username = username
        self.movie_id = movie_id
        self.remove_answer()

    def to_dict(self) -> dict:
        return {
            "question_type": self.question_type.value,
            "username": self.username,
            "movie_id": self.movie_id,
            "title": self.title,
            "answer": self.answer,
            "correct": self.correct,
            "answer_time": self.answer_time,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls: Self, data: dict) -> Self:
        question_type = QuestionType(data["question_type"])

        if question_type == QuestionType.MOVIE_BY_SLOGAN:
            question = MovieBySloganQuestion(title=data["title"], answer=data["answer"], slogan=data["slogan"])
        elif question_type in [QuestionType.MOVIE_BY_SHORT_DESCRIPTION, QuestionType.MOVIE_BY_DESCRIPTION]:
            question = MovieByDescriptionQuestion(title=data["title"], answer=data["answer"], description=SpoilerText.from_dict(data["description"]))
        elif question_type == QuestionType.MOVIE_BY_IMAGE:
            question = MovieByImageQuestion(title=data["title"], answer=data["answer"], image_url=data["image_url"])
        elif question_type == QuestionType.MOVIE_BY_ACTORS:
            actors = [Person.from_dict(actor) for actor in data["actors"]]
            question = MovieByActorsQuestion(title=data["title"], answer=data["answer"], actors=actors, hide_actor_photos=data["hide_actor_photos"])
        elif question_type == QuestionType.MOVIE_BY_CHARACTERS:
            question = MovieByCharactersQuestion(title=data["title"], answer=data["answer"], characters=data["characters"])
        else:
            raise ValueError(f'Invalid question_type "{question_type}"')

        question.question_type = question_type
        question.username = data["username"]
        question.movie_id = data["movie_id"]
        question.correct = data["correct"]
        question.answer_time = data["answer_time"]
        question.timestamp = data["timestamp"]

        return question

    def set_answer(self, answer: QuestionAnswer) -> None:
        self.correct = answer.correct
        self.answer_time = answer.answer_time
        self.timestamp = datetime.now()

    def remove_answer(self) -> None:
        self.correct = None
        self.answer_time = None
        self.timestamp = datetime.now()

    def is_valid(self, movie_ids: Set[int], settings: QuestionSettings) -> bool:
        return self.movie_id in movie_ids and self.question_type in settings.question_types

    def update(self, movie: Movie, person_id2person: Dict[int, Person], settings: QuestionSettings) -> Self:
        return self


@dataclass
class MovieBySloganQuestion(Question):
    slogan: str

    @classmethod
    def generate(cls: Self, movie: Movie, username: str) -> Self:
        question = cls(title=movie.get_question_title(" по слогану"), answer=movie.get_question_answer(), slogan=movie.slogan)
        question.init_base(question_type=QuestionType.MOVIE_BY_SLOGAN, username=username, movie_id=movie.movie_id)
        return question

    def update(self, movie: Movie, person_id2person: Dict[int, Person], settings: QuestionSettings) -> Self:
        super().update(movie, person_id2person, settings)
        self.title = movie.get_question_title(" по слогану")
        self.answer = movie.get_question_answer()
        self.slogan = movie.slogan
        return self

    def to_dict(self) -> dict:
        return {**super().to_dict(), "slogan": self.slogan}


@dataclass
class MovieByDescriptionQuestion(Question):
    description: SpoilerText

    @staticmethod
    def get_title(movie: Movie, question_type: QuestionType) -> Tuple[str, SpoilerText]:
        if question_type == QuestionType.MOVIE_BY_SHORT_DESCRIPTION:
            return movie.get_question_title(" по короткому описанию"), movie.short_description

        if question_type == QuestionType.MOVIE_BY_DESCRIPTION:
            return movie.get_question_title(" по описанию"), movie.description

        raise ValueError("Invalid question type")

    @classmethod
    def generate(cls: Self, movie: Movie, username: str, question_type: QuestionType) -> Self:
        title, description = cls.get_title(movie=movie, question_type=question_type)
        question = cls(title=title, answer=movie.get_question_answer(), description=description)
        question.init_base(question_type=question_type, username=username, movie_id=movie.movie_id)
        return question

    def update(self, movie: Movie, person_id2person: Dict[int, Person], settings: QuestionSettings) -> Self:
        super().update(movie, person_id2person, settings)
        self.title, self.description = self.get_title(movie=movie, question_type=self.question_type)
        self.answer = movie.get_question_answer()
        return self

    def to_dict(self) -> dict:
        return {**super().to_dict(), "description": self.description.to_dict()}


@dataclass
class MovieByImageQuestion(Question):
    image_url: str

    @classmethod
    def generate(cls: Self, movie: Movie, username: str) -> Self:
        question = cls(title=movie.get_question_title(" по кадру"), answer=movie.get_question_answer(), image_url=movie.get_random_image_url())
        question.init_base(question_type=QuestionType.MOVIE_BY_IMAGE, username=username, movie_id=movie.movie_id)
        return question

    def update(self, movie: Movie, person_id2person: Dict[int, Person], settings: QuestionSettings) -> Self:
        super().update(movie, person_id2person, settings)
        self.title = movie.get_question_title(" по кадру")
        self.answer = movie.get_question_answer()

        if self.image_url not in movie.image_urls:
            self.image_url = movie.get_random_image_url()

        return self

    def to_dict(self) -> dict:
        return {**super().to_dict(), "image_url": self.image_url}


@dataclass
class MovieByActorsQuestion(Question):
    actors: List[Person]
    hide_actor_photos: bool

    @classmethod
    def generate(cls: Self, movie: Movie, username: str, person_id2person: Dict[int, Person], hide_actor_photos: bool) -> Self:
        actors = [person_id2person[actor.person_id] for actor in movie.actors[:10][::-1]]
        question = cls(title=movie.get_question_title(" по актёрам"), answer=movie.get_question_answer(), actors=actors, hide_actor_photos=hide_actor_photos)
        question.init_base(question_type=QuestionType.MOVIE_BY_ACTORS, username=username, movie_id=movie.movie_id)
        return question

    def update(self, movie: Movie, person_id2person: Dict[int, Person], settings: QuestionSettings) -> Self:
        super().update(movie, person_id2person, settings)
        self.title = movie.get_question_title(" по актёрам")
        self.answer = movie.get_question_answer()
        self.actors = [person_id2person[actor.person_id] for actor in movie.actors[:10][::-1]]
        self.hide_actor_photos = settings.hide_actor_photos
        return self

    def to_dict(self) -> dict:
        return {**super().to_dict(), "actors": [actor.to_dict() for actor in self.actors], "hide_actor_photos": self.hide_actor_photos}


@dataclass
class MovieByCharactersQuestion(Question):
    characters: List[str]

    @classmethod
    def generate(cls: Self, movie: Movie, username: str) -> Self:
        characters = []

        for actor in movie.actors:
            if actor.description not in characters:
                characters.append(actor.description)

        question = cls(title=movie.get_question_title(" по именам персонажей"), answer=movie.get_question_answer(), characters=characters[:random.randint(3, 5)])
        question.init_base(question_type=QuestionType.MOVIE_BY_CHARACTERS, username=username, movie_id=movie.movie_id)
        return question

    def update(self, movie: Movie, person_id2person: Dict[int, Person], settings: QuestionSettings) -> Self:
        super().update(movie, person_id2person, settings)
        self.title = movie.get_question_title(" по именам персонажей")
        self.answer = movie.get_question_answer()
        return self

    def to_dict(self) -> dict:
        return {**super().to_dict(), "characters": self.characters}
