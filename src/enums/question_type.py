from enum import Enum


class QuestionType(Enum):
    MOVIE_BY_BANNER = "movie_by_banner"
    MOVIE_BY_SLOGAN = "movie_by_slogan"
    MOVIE_BY_SHORT_DESCRIPTION = "movie_by_short_description"
    MOVIE_BY_DESCRIPTION = "movie_by_description"
    MOVIE_BY_FACT = "movie_by_fact"
    MOVIE_BY_IMAGE = "movie_by_image"
    MOVIE_BY_ACTORS = "movie_by_actors"

    def to_rus(self) -> str:
        question_type2rus = {
            QuestionType.MOVIE_BY_BANNER: "КМС по баннеру",
            QuestionType.MOVIE_BY_SLOGAN: "КМС по слогану",
            QuestionType.MOVIE_BY_SHORT_DESCRIPTION: "КМС по короткому описанию",
            QuestionType.MOVIE_BY_DESCRIPTION: "КМС по описанию",
            QuestionType.MOVIE_BY_FACT: "КМС по факту",
            QuestionType.MOVIE_BY_IMAGE: "КМС по кадру",
            QuestionType.MOVIE_BY_ACTORS: "КМС по актёрам",
        }
        return question_type2rus[self]

    def to_query(self) -> dict:
        if self == QuestionType.MOVIE_BY_BANNER:
            return {"banner_url": {"$ne": None}}

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
            return {"actors": {"$ne": []}}

        raise ValueError(f'Invalid question type "{self}"')