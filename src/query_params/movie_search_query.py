import json
from dataclasses import dataclass
from typing import Optional

from fastapi import Query

from src.query_params.movie_search import MovieSearch


@dataclass
class MovieSearchQuery:
    query: Optional[str] = Query(None)
    order: Optional[str] = Query(None)
    order_type: Optional[int] = Query(None)
    movie_type: Optional[str] = Query(None)
    production: Optional[str] = Query(None)
    genre: Optional[str] = Query(None)
    years: Optional[str] = Query(None)
    votes: Optional[str] = Query(None)
    rating: Optional[str] = Query(None)
    rating_imdb: Optional[str] = Query(None)
    tracks: Optional[str] = Query(None)

    def is_empty(self) -> bool:
        fields = [
            self.query, self.order, self.order_type, self.movie_type, self.production, self.genre, self.years, self.votes, self.rating, self.rating_imdb, self.tracks
        ]

        for field in fields:
            if field is not None:
                return False

        return True

    def to_search_params(self) -> Optional[MovieSearch]:
        if self.is_empty():
            return None

        return MovieSearch(
            query=self.query if self.query is not None else "",
            order=self.order if self.order is not None else "rating.votes_kp",
            order_type=self.order_type if self.order_type is not None else -1,
            movie_type=json.loads(self.movie_type) if self.movie_type is not None else {},
            production=json.loads(self.production) if self.production is not None else {},
            genre=json.loads(self.genre) if self.genre is not None else {},
            years=json.loads(self.years) if self.years is not None else ["", ""],
            votes=json.loads(self.votes) if self.votes is not None else ["", ""],
            rating=json.loads(self.rating) if self.rating is not None else ["", ""],
            rating_imdb=json.loads(self.rating_imdb) if self.rating_imdb is not None else ["", ""],
            tracks=self.tracks if self.tracks in ["any", "with", "without"] else "any"
        )
