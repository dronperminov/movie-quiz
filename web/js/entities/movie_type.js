function MovieType(value) {
    this.value = value
    this.options = {
        "movie": "фильм",
        "cartoon": "мультфильм",
        "series": "сериал",
        "animated-series": "анимационный сериал",
        "anime": "аниме"
    }
}

MovieType.prototype.ToRus = function() {
    return this.options[this.value]
}
