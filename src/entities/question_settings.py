from dataclasses import dataclass
from datetime import date
from typing import Dict, Tuple, Union

from src.enums import MovieType, Production, QuestionType
from src.utils.queries import interval_query

QUESTION_YEARS = [("", 1979), (1980, 1989), (1990, 1999), (2000, 2009), (2010, 2014), (2015, 2019), (2020, "")]


@dataclass
class QuestionSettings:
    answer_time: float
    movie_types: Dict[MovieType, float]
    production: Dict[Production, float]
    votes: Tuple[Union[int, str], Union[int, str]]
    years: Dict[Union[Tuple[Union[int, str], Union[int, str]], str], float]
    question_types: Dict[QuestionType, float]
    hide_actor_photos: bool
    repeat_incorrect_probability: float

    def __post_init__(self) -> None:
        self.movie_types = self.__normalize_balance(self.movie_types)
        self.production = self.__normalize_balance(self.production)
        self.years = self.__normalize_balance({self.__fix_years_key(years): value for years, value in self.years.items()})
        self.question_types = self.__normalize_balance(self.question_types)

    def to_dict(self) -> dict:
        return {
            "answer_time": self.answer_time,
            "movie_types": {movie_type.value: value for movie_type, value in self.movie_types.items()},
            "production": {production.value: value for production, value in self.production.items()},
            "votes": self.votes,
            "years": [{"start_year": start_year, "end_year": end_year, "value": value} for (start_year, end_year), value in self.years.items()],
            "question_types": {question_type.value: value for question_type, value in self.question_types.items()},
            "hide_actor_photos": self.hide_actor_photos,
            "repeat_incorrect_probability": self.repeat_incorrect_probability,
        }

    @classmethod
    def from_dict(cls: "QuestionSettings", data: dict) -> "QuestionSettings":
        return cls(
            answer_time=data["answer_time"],
            movie_types={MovieType(movie_type): value for movie_type, value in data["movie_types"].items()},
            production={Production(production): value for production, value in data["production"].items()},
            votes=tuple(data["votes"]),
            years={(value["start_year"], value["end_year"]): value["value"] for value in data["years"]},
            question_types={QuestionType(question_type): value for question_type, value in data["question_types"].items()},
            hide_actor_photos=data["hide_actor_photos"],
            repeat_incorrect_probability=data["repeat_incorrect_probability"],
        )

    @classmethod
    def default(cls: "QuestionSettings") -> "QuestionSettings":
        return cls(
            answer_time=0,
            movie_types={movie_type: 1 / len(MovieType) for movie_type in MovieType},
            production={production: 1 / len(Production) for production in Production},
            votes=("", ""),
            years={(start_year, end_year): 1 / len(QUESTION_YEARS) for start_year, end_year in QUESTION_YEARS},
            question_types={question_type: 1 / len(QuestionType) for question_type in QuestionType},
            hide_actor_photos=False,
            repeat_incorrect_probability=0.04
        )

    def to_query(self) -> dict:
        query = {
            "movie_type": {"$in": [movie_type.value for movie_type in self.movie_types]},
            "production.0": {"$in": [production.value for production in self.production]},
            **interval_query("rating.votes_kp", self.votes),
            "year": {"$in": list(self.get_possible_years())},
            "$or": [question_type.to_query() for question_type in self.question_types]
        }

        return query

    def get_possible_years(self) -> Dict[int, tuple]:
        min_year, max_year = {"": 1900}, {"": date.today().year}
        years = {}

        for start_year, end_year in self.years:
            for year in range(min_year.get(start_year, start_year), max_year.get(end_year, end_year) + 1):
                years[year] = start_year, end_year

        return years

    def __fix_years_key(self, years: Union[Tuple[Union[int, str], Union[int, str]], str]) -> Tuple[Union[int, str], Union[int, str]]:
        if not isinstance(years, str):
            return years

        start, end = years.split("-")
        start = "" if start == "" else int(start)
        end = "" if end == "" else int(end)
        return start, end

    def __normalize_balance(self, balance_dict: dict) -> dict:
        total = sum(balance_dict.values())
        if total == 0:
            total = 1

        return {enum: value / total for enum, value in balance_dict.items() if value > 0}
