import random
from dataclasses import dataclass
from typing import List

from src.entities.actor import Actor
from src.entities.metadata import Metadata
from src.entities.rating import Rating
from src.entities.source import Source
from src.entities.spoiler_text import SpoilerText
from src.enums import Genre, MovieType, Production, QuestionType


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
    sequels: List[int]
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
            "sequels": self.sequels,
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
            sequels=data["sequels"],
            metadata=Metadata.from_dict(data["metadata"])
        )

    def get_diff(self, data: dict) -> dict:
        movie_data = self.to_dict()
        diff = {}

        fields = [
            "name", "movie_type", "year", "slogan", "description", "short_description", "production", "countries", "genres", "actors", "directors",
            "duration", "rating", "image_urls", "poster_url", "banner_url", "facts", "cites", "tracks", "alternative_names", "sequels"
        ]

        for field in fields:
            if field in data and movie_data[field] != data[field]:
                diff[field] = {"prev": movie_data[field], "new": data[field]}

        return diff

    def get_question_types(self) -> List[QuestionType]:
        question_types = []

        if self.slogan:
            question_types.append(QuestionType.MOVIE_BY_SLOGAN)

        if self.short_description.text:
            question_types.append(QuestionType.MOVIE_BY_SHORT_DESCRIPTION)

        if self.description.text:
            question_types.append(QuestionType.MOVIE_BY_DESCRIPTION)

        if self.image_urls:
            question_types.append(QuestionType.MOVIE_BY_IMAGE)

        if self.actors and self.movie_type in [MovieType.MOVIE, MovieType.SERIES]:
            question_types.append(QuestionType.MOVIE_BY_ACTORS)

        if self.actors and self.movie_type != MovieType.ANIME:
            question_types.append(QuestionType.MOVIE_BY_CHARACTERS)

        if self.cites:
            question_types.append(QuestionType.MOVIE_BY_CITE)

        if self.tracks:
            question_types.append(QuestionType.MOVIE_BY_TRACK)

        return question_types

    def get_question_title(self, end: str = "") -> str:
        return f"Назовите {self.movie_type.to_rus()}{end}"

    def get_question_answer(self) -> str:
        return f'<a class="link" href="/movies/{self.movie_id}">{self.name}</a>'

    def get_random_image_url(self) -> str:
        return random.choice(self.image_urls)
