from enum import Enum


class MovieType(Enum):
    MOVIE = "movie"
    CARTOON = "cartoon"
    SERIES = "series"
    ANIMATED_SERIES = "animated-series"
    ANIME = "anime"

    def to_rus(self) -> str:
        movie_type2rus = {
            MovieType.MOVIE: "фильм",
            MovieType.CARTOON: "мультфильм",
            MovieType.SERIES: "сериал",
            MovieType.ANIMATED_SERIES: "анимационный сериал",
            MovieType.ANIME: "аниме"
        }

        return movie_type2rus[self]

    @classmethod
    def from_kinopoisk(cls: "MovieType", movie_type: str) -> "MovieType":
        kinopoisk2movie_type = {
            "movie": MovieType.MOVIE,
            "tv-series": MovieType.SERIES,
            "cartoon": MovieType.CARTOON,
            "animated-series": MovieType.ANIMATED_SERIES,
            "anime": MovieType.ANIME
        }

        return kinopoisk2movie_type[movie_type]
