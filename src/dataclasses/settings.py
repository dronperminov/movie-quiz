from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src import constants
from src.utils.common import get_default_question_years
from src.utils.film import production_to_query


@dataclass
class Settings:
    theme: str
    question_years: List[List[int]]
    questions: List[str]
    movie_productions: List[str]
    movie_types: List[str]
    top_lists: List[str]
    hide_actors: bool
    last_update: datetime
    show_questions_count: bool
    facts_mode: str

    @classmethod
    def from_dict(cls: "Settings", data: Optional[dict]) -> "Settings":
        if data is None:
            data = {}

        theme = data.get("theme", "light")
        question_years = data.get("question_years", get_default_question_years())
        questions = data.get("questions", constants.QUESTIONS)
        movie_productions = data.get("movie_productions", constants.PRODUCTIONS)
        movie_types = data.get("movie_types", constants.MOVIE_TYPES)
        top_lists = data.get("top_lists", [])
        hide_actors = data.get("hide_actors", True)
        last_update = data.get("last_update", datetime(1900, 1, 1))
        show_questions_count = data.get("show_questions_count", True)
        facts_mode = data.get("facts_mode", constants.SHOW_ALL_FACTS_MODE)

        return cls(theme, question_years, questions, movie_productions, movie_types, top_lists, hide_actors, last_update, show_questions_count, facts_mode)

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "question_years": self.question_years,
            "questions": self.questions,
            "movie_productions": self.movie_productions,
            "movie_types": self.movie_types,
            "top_lists": self.top_lists,
            "hide_actors": self.hide_actors,
            "last_update": self.last_update,
            "show_questions_count": self.show_questions_count,
            "facts_mode": self.facts_mode
        }

    def to_films_query(self) -> dict:
        query = {
            "$and": [
                {"$or": [{"year": {"$gte": start_year, "$lte": end_year}} for start_year, end_year in self.question_years]},
                {"$or": [production_to_query(production) for production in self.movie_productions]},
                {"type": {"$in": self.movie_types}}
            ]
        }

        if self.top_lists:
            query["$and"].append({"tops": {"$in": self.top_lists}})

        return query

    def to_query(self, question_type: str = "") -> dict:
        question_types = [question_type] if question_type else self.questions

        query = self.to_films_query()
        query["$and"].append({"$or": [self.question_to_query(question_type) for question_type in question_types]})
        return query

    def question_to_query(self, question_type: str) -> dict:
        if question_type == constants.QUESTION_MOVIE_BY_BANNER:
            return {"banner": {"$exists": True}}

        if question_type == constants.QUESTION_MOVIE_BY_SLOGAN:
            return {"slogan": {"$exists": True, "$ne": ""}}

        if question_type == constants.QUESTION_MOVIE_BY_DESCRIPTION:
            return {"description.value": {"$ne": ""}}

        if question_type == constants.QUESTION_MOVIE_BY_SHORT_DESCRIPTION:
            return {"shortDescription.value": {"$ne": ""}}

        if question_type == constants.QUESTION_MOVIE_BY_FACTS:
            return {"facts": {"$exists": True, "$nin": [[], None]}}

        if question_type == constants.QUESTION_MOVIE_BY_AUDIO:
            return {"audios": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_ACTORS:
            return {"actors": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_IMAGES:
            return {"images": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_CITE:
            return {"cites": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_FIRST_LETTERS:
            return {"name": {"$exists": True, "$regex": "[a-zA-ZА-Яа-яёЁ]+[^a-zA-ZА-Яа-яёЁ]+[a-zA-ZА-Яа-яёЁ]+"}}

        if question_type == constants.QUESTION_YEAR_BY_MOVIE:
            return {
                "$or": [
                    self.question_to_query(constants.QUESTION_MOVIE_BY_BANNER),
                    self.question_to_query(constants.QUESTION_MOVIE_BY_SLOGAN),
                    self.question_to_query(constants.QUESTION_MOVIE_BY_DESCRIPTION)
                ]
            }

        raise ValueError(f'Unhandled question_type "{question_type}"')
