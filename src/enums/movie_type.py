from enum import Enum


class MovieType(Enum):
    FILM = "film"
    CARTOON = "cartoon"
    SERIES = "series"
    ANIMATED_SERIES = "animated-series"
    ANIME = "anime"

    def to_rus(self) -> str:
        movie_type2rus = {
            MovieType.FILM: "фильм",
            MovieType.CARTOON: "мультфильм",
            MovieType.SERIES: "сериал",
            MovieType.ANIMATED_SERIES: "анимационный сериал",
            MovieType.ANIME: "аниме"
        }

        return movie_type2rus[self]
