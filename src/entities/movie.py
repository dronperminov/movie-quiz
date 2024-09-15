from dataclasses import dataclass
from typing import List

from src.entities.actor import Actor
from src.entities.metadata import Metadata
from src.entities.rating import Rating
from src.entities.source import Source
from src.entities.spoiler_text import SpoilerText
from src.enums import Genre, MovieType
from src.enums.production import Production


@dataclass
class Movie:
    movie_id: int
    name: str
    source: Source
    movie_type: MovieType
    year: int
    slogan: str
    description: SpoilerText
    short_description: SpoilerText
    production: List[Production]
    countries: List[str]
    genres: List[Genre]
    actors: List[Actor]
    directors: List[Actor]
    duration: float
    rating: Rating
    image_urls: List[str]
    poster_url: str
    banner_url: str
    facts: List[SpoilerText]
    cites: List[int]
    tracks: List[int]
    alternative_names: List[str]
    metadata: Metadata

    def to_dict(self) -> dict:
        return {
            "movie_id": self.movie_id,
            "name": self.name,
            "source": self.source.to_dict(),
            "movie_type": self.movie_type.value,
            "year": self.year,
            "slogan": self.slogan,
            "description": self.description.to_dict(),
            "short_description": self.short_description.to_dict(),
            "production": [production.value for production in self.production],
            "countries": self.countries,
            "genres": [genre.value for genre in self.genres],
            "actors": [actor.to_dict() for actor in self.actors],
            "directors": [director.to_dict() for director in self.directors],
            "duration": self.duration,
            "rating": self.rating.to_dict(),
            "image_urls": self.image_urls,
            "poster_url": self.poster_url,
            "banner_url": self.banner_url,
            "facts": [fact.to_dict() for fact in self.facts],
            "cites": self.cites,
            "tracks": self.tracks,
            "alternative_names": self.alternative_names,
            "metadata": self.metadata.to_dict()
        }

    @classmethod
    def from_dict(cls: "Movie", data: dict) -> "Movie":
        return cls(
            movie_id=data["movie_id"],
            name=data["name"],
            source=Source.from_dict(data["source"]),
            movie_type=MovieType(data["movie_type"]),
            year=data["year"],
            slogan=data["slogan"],
            description=SpoilerText.from_dict(data["description"]),
            short_description=SpoilerText.from_dict(data["short_description"]),
            production=[Production(production) for production in data["production"]],
            countries=data["countries"],
            genres=[Genre(genre) for genre in data["genres"]],
            actors=[Actor.from_dict(actor) for actor in data["actors"]],
            directors=[Actor.from_dict(director) for director in data["directors"]],
            duration=data["duration"],
            rating=Rating.from_dict(data["rating"]),
            image_urls=data["image_urls"],
            poster_url=data["poster_url"],
            banner_url=data["banner_url"],
            facts=[SpoilerText.from_dict(fact) for fact in data["facts"]],
            cites=data["cites"],
            tracks=data["tracks"],
            alternative_names=data["alternative_names"],
            metadata=Metadata.from_dict(data["metadata"])
        )

    def get_diff(self, data: dict) -> dict:
        movie_data = self.to_dict()
        diff = {}

        fields = [
            "name", "movie_type", "year", "slogan", "description", "short_description", "production", "countries", "genres", "actors",
            "directors", "duration", "rating", "image_urls", "poster_url", "banner_url", "facts", "cites", "tracks", "alternative_names"
        ]

        for field in fields:
            if field in data and movie_data[field] != data[field]:
                diff[field] = {"prev": movie_data[field], "new": data[field]}

        return diff
