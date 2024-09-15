from enum import Enum


class Genre(Enum):
    ANIME = "anime"
    BIOGRAPHY = "biography"
    ACTION = "action"
    WESTERN = "western"
    WAR = "war"
    DETECTIVE = "detective"
    CHILDREN = "children"
    ADULT = "adult"
    DOCUMENTARY = "documentary"
    DRAMA = "drama"
    GAME = "game"
    HISTORY = "history"
    COMEDY = "comedy"
    CONCERT = "concert"
    SHORT_FILM = "short_film"
    CRIME = "crime"
    MELODRAMA = "melodrama"
    MUSIC = "music"
    CARTOON = "cartoon"
    MUSICAL = "musical"
    NEWS = "news"
    ADVENTURE = "adventure"
    REALITY_TV = "reality_tv"
    FAMILY = "family"
    SPORTS = "sports"
    TALK_SHOW = "talk_show"
    THRILLER = "thriller"
    HORROR = "horror"
    SCI_FI = "sci-fi"
    NOIR = "noir"
    FANTASY = "fantasy"
    CEREMONY = "ceremony"

    def to_rus(self) -> str:
        genre2rus = {
            Genre.ANIME: "аниме",
            Genre.BIOGRAPHY: "биография",
            Genre.ACTION: "боевик",
            Genre.WESTERN: "вестерн",
            Genre.WAR: "военный",
            Genre.DETECTIVE: "детектив",
            Genre.CHILDREN: "детский",
            Genre.ADULT: "для взрослых",
            Genre.DOCUMENTARY: "документальный",
            Genre.DRAMA: "драма",
            Genre.GAME: "игра",
            Genre.HISTORY: "история",
            Genre.COMEDY: "комедия",
            Genre.CONCERT: "концерт",
            Genre.SHORT_FILM: "короткометражка",
            Genre.CRIME: "криминал",
            Genre.MELODRAMA: "мелодрама",
            Genre.MUSIC: "музыка",
            Genre.CARTOON: "мультфильм",
            Genre.MUSICAL: "мюзикл",
            Genre.NEWS: "новости",
            Genre.ADVENTURE: "приключения",
            Genre.REALITY_TV: "реальное ТВ",
            Genre.FAMILY: "семейный",
            Genre.SPORTS: "спорт",
            Genre.TALK_SHOW: "ток-шоу",
            Genre.THRILLER: "триллер",
            Genre.HORROR: "ужасы",
            Genre.SCI_FI: "фантастика",
            Genre.NOIR: "нуар",
            Genre.FANTASY: "фэнтези",
            Genre.CEREMONY: "церемония"
        }

        return genre2rus[self]
