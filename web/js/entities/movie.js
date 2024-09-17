function Movie(data, params) {
    this.movieId = data.movie_id
    this.name = data.name
    this.source = data.source
    this.movieType = new MovieType(data.movie_type)
    this.year = data.year
    this.slogan = data.slogan
    this.description = data.description
    this.shortDescription = data.short_description
    this.production = new ProductionList(data.production)
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

Movie.prototype.BuildPage = function(blockId = "movie") {
    let movie = document.getElementById(blockId)

    let movieImage = MakeElement("movie-image", movie)
    if (this.bannerUrl !== null)
        MakeElement("", movieImage, {src: this.bannerUrl, loading: "lazy"}, "img")
    this.BuildRating(movieImage)

    this.BuildName(movie, "movie-name")

    MakeElement("movie-main-info", movie, {innerText: this.GetMainInfo()})
    MakeElement("movie-sub-info", movie, {innerText: this.GetSubInfo()})

    if (this.shortDescription.text.length > 0)
        MakeElement("movie-short-description", movie, {innerText: this.shortDescription.text})

    if (this.description.text.length > 0) {
        let description = MakeElement("movie-description", movie, {innerText: this.description.text})
        let link = MakeElement("movie-description-link", movie, {innerText: "Полное описание"})
        link.addEventListener("click", () => {
            description.classList.toggle("movie-description-open")
            link.innerText = description.classList.contains("movie-description-open") ? "Свернуть" : "Полное описание"
        })
    }

    if (this.slogan.length > 0)
        MakeElement("movie-slogan", movie, {innerHTML: `<b>Слоган</b>: ${this.slogan}`})

    this.BuildPageImages(movie)
    this.BuildPagePersons(movie, "Актёры", this.actors)
    this.BuildPagePersons(movie, "Режиссёр" + (this.directors.length > 1 ? "ы" : ""), this.directors)
    this.BuildPageFacts(movie)
}

Movie.prototype.BuildPageImages = function(parent) {
    if (this.imageUrls.length == 0)
        return

    MakeElement("movie-header", parent, {innerText: "Кадры"})

    let images = MakeElement("movie-images", parent)
    let container = MakeElement("movie-images-container", images)

    for (let imageUrl of this.imageUrls)
        MakeElement("", container, {src: imageUrl, loading: "lazy"}, "img")
}

Movie.prototype.BuildPagePersons = function(parent, header, persons) {
    if (persons.length == 0)
        return

    MakeElement("movie-header", parent, {innerText: header})

    let images = MakeElement("movie-images", parent)
    let container = MakeElement("movie-images-container", images)

    for (let actor of persons) {
        let actorBlock = MakeElement("movie-actor", container)
        let person = this.params.personId2person[`${actor.person_id}`]

        let link = MakeElement("", actorBlock, {href: `/persons/${actor.person_id}`}, "a")
        MakeElement("", link, {src: person.photo_url, loading: "lazy"}, "img")
        MakeElement("link", actorBlock, {href: `/persons/${actor.person_id}`, innerText: person.name}, "a")
    }
}

Movie.prototype.BuildPageFacts = function(parent) {
    if (this.facts.length == 0)
        return

    MakeElement("movie-header", parent, {innerText: "Факты"})

    let facts = MakeElement("movie-facts", parent)

    for (let fact of this.facts)
        MakeElement("movie-fact", facts, {innerText: fact.text})
}

Movie.prototype.BuildInfo = function() {
    let info = MakeElement("info", null, {"id": `info-movie-${this.movieId}`})
    let closeIcon = MakeElement("close-icon", info, {title: "Закрыть"})

    let infoImage = MakeElement("info-image", info)
    MakeElement("", infoImage, {src: this.bannerUrl, loading: "lazy"}, "img")

    this.BuildName(info, "info-header-line")

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

    MakeElement("info-line", info, {innerHTML: `<b>Производство</b>: ${this.production.ToRus()}`})
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
    this.BuildAdmin(info)

    return info
}

Movie.prototype.BuildName = function(parent, className) {
    if (this.source.name == "kinopoisk") {
        let header = MakeElement(className, parent)
        let link = MakeElement("", header, {href: `https://kinopoisk.ru/film/${this.source.kinopoisk_id}`, target: "_blank"}, "a")
        let img = MakeElement("", link, {src: "/images/kinopoisk.svg"}, "img")
        let span = MakeElement("", header, {innerText: ` ${this.name}`}, "span")
    }
    else {
        MakeElement(className, parent, {innerHTML: this.name})
    }
}

Movie.prototype.BuildInfoImages = function(parent) {
    if (this.imageUrls.length == 0)
        return

    let images = MakeElement("info-images", parent)
    MakeElement("info-line", images, {innerHTML: "<b>Кадры</b>"})
    let imagesDiv = MakeElement("info-images-container", images)

    for (let imageUrl of this.imageUrls) {
        let infoImage = MakeElement("info-image", imagesDiv)
        MakeElement("", infoImage, {src: imageUrl, loading: "lazy"}, "img")
    }
}

Movie.prototype.BuildInfoActors = function(parent) {
    if (this.actors.length == 0)
        return

    let actors = MakeElement("info-images", parent)
    MakeElement("info-line", actors, {innerHTML: "<b>Актёры</b>"})
    let actorsDiv = MakeElement("info-images-container", actors)

    for (let actor of this.actors) {
        let infoImage = MakeElement("info-image info-actor", actorsDiv)
        let person = this.params.personId2person[`${actor.person_id}`]

        let link = MakeElement("", infoImage, {href: `/persons/${actor.person_id}`}, "a")
        MakeElement("", link, {src: person.photo_url, loading: "lazy"}, "img")
        MakeElement("link", infoImage, {href: `/persons/${actor.person_id}`, innerText: person.name}, "a")
    }
}

Movie.prototype.BuildAdmin = function(parent) {
    let adminBlock = MakeElement("admin-buttons admin-block", parent)
    let buttons = []

    let historyButton = MakeElement("basic-button gradient-button", adminBlock, {innerText: "История изменений"}, "button")
    buttons.push(historyButton)
    historyButton.addEventListener("click", () => ShowHistory(`/movie-history/${this.movieId}`))

    if (this.source.name == "kinopoisk") {
        let button = MakeElement("basic-button gradient-button", adminBlock, {innerText: "Распарсить"}, "button")
        buttons.push(button)
        button.addEventListener("click", () => ParseMovies(buttons, [this.source.kinopoisk_id]))
    }
}

Movie.prototype.BuildRating = function(parent) {
    let color = this.GetRatingColor(this.rating.rating_kp)
    let rating = Math.round(this.rating.rating_kp * 10)

    MakeElement("movie-rating", parent, {innerText: `${Math.floor(rating / 10)}.${rating % 10}`, style: `background-color: ${color}`})
}

Movie.prototype.GetShortInfo = function() {
    return [this.countries.slice(0, 2).join(", "), this.FormatVotes()].join(" • ")
}

Movie.prototype.GetStats = function() {
    return [this.year, this.genres.ToRus(2), this.movieType.ToRus()].join(" | ")
}

Movie.prototype.GetMainInfo = function() {
    let info = [this.year, this.genres.ToRus(2)]

    if (this.duration)
        info.push(this.FormatDuration())

    return info.join(" • ")
}

Movie.prototype.GetSubInfo = function() {
    return [this.movieType.ToRus(), this.countries.slice(0, 2).join(", "), this.FormatVotes()].join(" • ")
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
    let directors = []

    for (let director of this.directors) {
        let person = this.params.personId2person[`${director.person_id}`]
        directors.push(`<a class="link" href="/persons/${person.person_id}">${person.name}</a>`)
    }

    return directors.join(", ")
}
