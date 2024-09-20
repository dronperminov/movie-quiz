from enum import Enum

from src.enums import MovieType


class QuestionType(Enum):
    MOVIE_BY_SLOGAN = "movie_by_slogan"
    MOVIE_BY_SHORT_DESCRIPTION = "movie_by_short_description"
    MOVIE_BY_DESCRIPTION = "movie_by_description"
    MOVIE_BY_FACT = "movie_by_fact"
    MOVIE_BY_IMAGE = "movie_by_image"
    MOVIE_BY_ACTORS = "movie_by_actors"
    MOVIE_BY_CHARACTERS = "movie_by_characters"
    MOVIE_BY_CITE = "movie_by_cite"
    MOVIE_BY_TRACK = "movie_by_track"

    def to_rus(self) -> str:
        question_type2rus = {
            QuestionType.MOVIE_BY_SLOGAN: "КМС по слогану",
            QuestionType.MOVIE_BY_SHORT_DESCRIPTION: "КМС по короткому описанию",
            QuestionType.MOVIE_BY_DESCRIPTION: "КМС по описанию",
            QuestionType.MOVIE_BY_FACT: "КМС по факту",
            QuestionType.MOVIE_BY_IMAGE: "КМС по кадру",
            QuestionType.MOVIE_BY_ACTORS: "КМС по актёрам",
            QuestionType.MOVIE_BY_CHARACTERS: "КМС по именам персонажей",
            QuestionType.MOVIE_BY_CITE: "КМС по цитате",
            QuestionType.MOVIE_BY_TRACK: "КМС по треку"
        }
        return question_type2rus[self]

    def to_query(self) -> dict:
        if self == QuestionType.MOVIE_BY_SLOGAN:
            return {"slogan": {"$ne": ""}}

        if self == QuestionType.MOVIE_BY_SHORT_DESCRIPTION:
            return {"short_description.text": {"$ne": ""}}

        if self == QuestionType.MOVIE_BY_DESCRIPTION:
            return {"description.text": {"$ne": ""}}

        if self == QuestionType.MOVIE_BY_FACT:
            return {"facts": {"$ne": []}}

        if self == QuestionType.MOVIE_BY_IMAGE:
            return {"image_urls": {"$ne": []}}

        if self == QuestionType.MOVIE_BY_ACTORS:
            return {"actors": {"$ne": []}, "movie_type": {"$in": [MovieType.MOVIE.value, MovieType.SERIES.value]}}

        if self == QuestionType.MOVIE_BY_CHARACTERS:
            return {"actors": {"$ne": []}, "actors.description": {"$ne": {"$regex": "озвучка"}}, "movie_type": {"$ne": MovieType.ANIME.value}}

        if self == QuestionType.MOVIE_BY_CITE:
            return {"cites": {"$ne": []}}

        if self == QuestionType.MOVIE_BY_TRACK:
            return {"tracks": {"$ne": []}}

        raise ValueError(f'Invalid question type "{self}"')
