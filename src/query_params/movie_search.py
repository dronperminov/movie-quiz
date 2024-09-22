import re
from dataclasses import dataclass, field
from typing import Dict, List, Union

from src.enums import MovieType, Production
from src.utils.queries import enum_query, interval_query


@dataclass
class MovieSearch:
    query: str = ""
    order: str = "rating.votes_kp"
    order_type: int = -1
    movie_type: Dict[MovieType, bool] = field(default_factory=dict)
    production: Dict[Production, bool] = field(default_factory=dict)
    years: List[Union[str, float, int]] = field(default_factory=lambda: ["", ""])
    votes: List[Union[str, float, int]] = field(default_factory=lambda: ["", ""])
    rating: List[Union[str, float, int]] = field(default_factory=lambda: ["", ""])
    rating_imdb: List[Union[str, float, int]] = field(default_factory=lambda: ["", ""])
    tracks: str = "any"
    page: int = 0
    page_size: int = 20

    def to_query(self) -> dict:
        query = {
            **self.__to_name_query(),
            **self.__to_tracks_query(),
            **enum_query("movie_type", self.movie_type),
            **enum_query("production", self.production),
            **interval_query("year", self.years),
            **interval_query("rating.votes_kp", self.votes),
            **interval_query("rating.rating_kp", self.rating),
            **interval_query("rating.rating_imdb", self.rating_imdb),
        }

        return query

    def __to_name_query(self) -> dict:
        if not self.query:
            return {}

        if re.fullmatch(r"/[^/]+/", self.query):
            return {"name": {"$regex": self.query[1:-1], "$options": "i"}}

        if re.fullmatch(r"\^[^^]+", self.query):
            return {"name": {"$regex": fr"^{re.escape(self.query[1:])}", "$options": "i"}}

        if re.fullmatch(r"[^$]+\$", self.query):
            return {"name": {"$regex": fr"{re.escape(self.query[:-1])}$", "$options": "i"}}

        return {"name": {"$regex": re.escape(self.query), "$options": "i"}}

    def __to_tracks_query(self) -> dict:
        if self.tracks == "without":
            return {"tracks": []}

        if self.tracks == "with":
            return {"tracks": {"$ne": []}}

        return {}
