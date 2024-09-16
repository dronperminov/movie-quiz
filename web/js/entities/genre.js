function Genre(value) {
    this.value = value
    this.options = {
        "anime": "аниме",
        "biography": "биография",
        "action": "боевик",
        "western": "вестерн",
        "war": "военный",
        "detective": "детектив",
        "children": "детский",
        "adult": "для взрослых",
        "documentary": "документальный",
        "drama": "драма",
        "game": "игра",
        "history": "история",
        "comedy": "комедия",
        "concert": "концерт",
        "short_film": "короткометражка",
        "crime": "криминал",
        "melodrama": "мелодрама",
        "music": "музыка",
        "cartoon": "мультфильм",
        "musical": "мюзикл",
        "news": "новости",
        "adventure": "приключения",
        "reality_tv": "реальное ТВ",
        "family": "семейный",
        "sports": "спорт",
        "talk_show": "ток-шоу",
        "thriller": "триллер",
        "horror": "ужасы",
        "sci-fi": "фантастика",
        "noir": "нуар",
        "fantasy": "фэнтези",
        "ceremony": "церемония"
    }
}

Genre.prototype.ToRus = function() {
    return this.options[this.value]
}

function GenreList(genres) {
    this.genres = genres.map(genre => new Genre(genre))
}

GenreList.prototype.ToRus = function() {
    return this.genres.map(genre => genre.ToRus()).join(", ")
}
