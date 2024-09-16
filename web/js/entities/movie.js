function Movie(data, params) {
    this.movieId = data.movie_id
    this.name = data.name
    this.source = data.source
    this.movieType = new MovieType(data.movie_type)
    this.year = data.year
    this.slogan = data.slogan
    this.description = data.description
    this.shortDescription = data.short_description
    this.production = data.production
    this.countries = data.countries
    this.genres = new GenreList(data.genres)
    this.actors = data.actors
    this.directors = data.directors
    this.duration = data.duration
    this.rating = data.rating
    this.imageUrls = data.image_urls
    this.posterUrl = data.poster_url
    this.bannerUrl = data.banner_url
    this.facts = data.facts
    this.cites = data.cites
    this.tracks = data.tracks
    this.alternativeNames = data.alternative_names
    this.metadata = new Metadata(data.metadata, "Добавлен", "Обновлён")
    this.params = params
}

Movie.prototype.Build = function() {
    let movie = MakeElement("movie")
    let movieImage = MakeElement("movie-image", movie)
    let movieImageLink = MakeElement("", movieImage, {href: `/movies/${this.movieId}`}, "a")
    MakeElement("", movieImageLink, {src: this.posterUrl, loading: "lazy"}, "img")
    this.BuildRating(movieImage)

    let movieInfo = MakeElement("movie-data", movie)

    let movieName = MakeElement("movie-name", movieInfo)
    MakeElement("", movieName, {href: `/movies/${this.movieId}`, innerText: this.name}, "a")

    MakeElement("movie-stats", movieInfo, {innerHTML: this.GetStats()})
    MakeElement("movie-short-info", movieInfo, {innerHTML: this.GetShortInfo()})

    let movieControls = MakeElement("movie-controls", movieInfo)
    let div = MakeElement("", movieControls)
    MakeElement("gradient-link", div, {href: `/movies/${this.movieId}`, innerText: "Смотреть"}, "a")

    let movieMenu = MakeElement("movie-menu", movie)
    let verticalHam = MakeElement("vertical-ham", movieMenu, {innerHTML: "<div></div><div></div><div></div>"})
    verticalHam.addEventListener("click", () => infos.Show(`movie-${this.movieId}`))

    return movie
}

Movie.prototype.BuildInfo = function() {
    let info = MakeElement("info", null, {"id": `info-movie-${this.movieId}`})
    let closeIcon = MakeElement("close-icon", info, {title: "Закрыть"})

    let infoImage = MakeElement("info-image", info)
    MakeElement("", infoImage, {src: this.bannerUrl, loading: "lazy"}, "img")

    if (this.source.name == "kinopoisk") {
        let header = MakeElement("info-header-line", info)
        let link = MakeElement("", header, {href: `https://kinopoisk.ru/film/${this.source.kinopoisk_id}`, target: "_blank"}, "a")
        let img = MakeElement("", link, {src: "/images/kinopoisk.svg"}, "img")
        let span = MakeElement("", header, {innerText: ` ${this.name}`}, "span")
    }
    else {
        MakeElement("info-header-line", info, {innerHTML: this.name})
    }

    let rating = MakeElement("info-line", info, {innerHTML: `<b>Рейтинг КП</b>: `})
    MakeElement("info-line", info, {innerHTML: `<b>Тип КМС</b>: ${this.movieType.ToRus()}`})
    MakeElement("info-line", info, {innerHTML: `<b>Год выхода</b>: ${this.year}`})
    this.BuildRating(rating)

    if (this.slogan.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Слоган</b>: ${this.slogan}`})

    if (this.description.text.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Описание</b>: ${this.description.text}`})

    if (this.shortDescription.text.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Короткое описание</b>: ${this.shortDescription.text}`})

    MakeElement("info-line", info, {innerHTML: `<b>Стран${this.countries.length == 1 ? "а" : "ы"}</b>: ${this.countries.join(", ")}`})
    MakeElement("info-line", info, {innerHTML: `<b>Жанр${this.genres.genres.length == 1 ? "" : "ы"}</b>: ${this.genres.ToRus()}`})
    MakeElement("info-line", info, {innerHTML: `<b>Режиссёр${this.directors.length == 1 ? "" : "ы"}</b>: ${this.GetDirectors()}`})

    if (this.duration)
        MakeElement("info-line", info, {innerHTML: `<b>Длительность</b>: ${this.FormatDuration()}`})

    this.BuildInfoImages(info)
    this.BuildInfoActors(info)

    if (this.alternativeNames.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Другие названия</b>: ${this.alternativeNames.join(", ")}`})

    this.metadata.BuildInfo(info)

    return info
}

Movie.prototype.BuildInfoImages = function(parent) {
    let images = MakeElement("info-images", parent)
    MakeElement("info-line", images, {innerHTML: "<b>Кадры</b>"})
    let imagesDiv = MakeElement("info-images-container", images)

    for (let imageUrl of this.imageUrls) {
        let infoImage = MakeElement("info-image", imagesDiv)
        MakeElement("", infoImage, {src: imageUrl, loading: "lazy"}, "img")
    }
}

Movie.prototype.BuildInfoActors = function(parent) {
    let actors = MakeElement("info-images", parent)
    MakeElement("info-line", actors, {innerHTML: "<b>Актёры</b>"})
    let actorsDiv = MakeElement("info-images-container", actors)

    for (let actor of this.actors) {
        let infoImage = MakeElement("info-image info-actor", actorsDiv)

        let person = this.params.personId2person[`${actor.person_id}`]
        MakeElement("", infoImage, {src: person.photo_url, loading: "lazy"}, "img")
        MakeElement("", infoImage, {innerText: person.name})
    }
}

Movie.prototype.BuildRating = function(parent) {
    let color = this.GetRatingColor(this.rating.rating_kp)
    let rating = Math.round(this.rating.rating_kp * 10)

    MakeElement("movie-rating", parent, {innerText: `${Math.floor(rating / 10)}.${rating % 10}`, style: `background-color: ${color}`})
}

Movie.prototype.GetShortInfo = function() {
    let country = this.countries[0]
    let genre = this.genres.genres[0].ToRus()
    return [country, genre].join(" • ")
}

Movie.prototype.GetStats = function() {
    return [this.year, this.FormatVotes(), this.movieType.ToRus()].join(" | ")
}

Movie.prototype.FormatVotes = function() {
    if (this.rating.votes_kp >= 1000000)
        return `${Round(this.rating.votes_kp / 1000000)}M оценок`

    if (this.rating.votes_kp >= 1000)
        return `${Round(this.rating.votes_kp / 1000)}K оценок`

    return GetWordForm(this.rating.votes_kp, ['оценка', 'оценки', 'оценок'])
}

Movie.prototype.GetRatingColor = function(rating) {
    if (rating > 7.5)
        return "#3bb33b"

    if (rating > 6)
        return "#ff9800"

    if (rating > 3.5)
        return "#f44336"

    return "#545454"
}

Movie.prototype.FormatDuration = function() {
    let duration = Math.round(this.duration)
    let hours = `${Math.floor(duration / 60)}`
    let minutes = `${duration % 60}`.padStart(2, '0')

    return `${hours} ч. ${minutes} мин.`
}

Movie.prototype.GetDirectors = function() {
    return this.directors.map(director => this.params.personId2person[`${director.person_id}`].name).join(", ")
}
