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
    let movieMain = MakeElement("movie-main", movie)

    let movieImage = MakeElement("movie-image", movieMain)
    let movieImageLink = MakeElement("", movieImage, {href: `/movies/${this.movieId}`}, "a")
    MakeElement("", movieImageLink, {src: this.posterUrl, loading: "lazy"}, "img")
    this.BuildRating(movieImage)

    let movieInfo = MakeElement("movie-data", movieMain)

    let movieName = MakeElement("movie-name", movieInfo)
    this.BuildScale(movieName)
    MakeElement("", movieName, {href: `/movies/${this.movieId}`, innerText: this.name}, "a")

    MakeElement("movie-stats", movieInfo, {innerHTML: this.GetStats()})
    MakeElement("movie-short-info", movieInfo, {innerHTML: this.GetShortInfo()})

    let movieControls = MakeElement("movie-controls", movieInfo)
    let div = MakeElement("", movieControls)
    MakeElement("gradient-link", div, {href: `/movies/${this.movieId}`, innerText: "Смотреть"}, "a")

    let movieMenu = MakeElement("movie-menu", movieMain)
    let verticalHam = MakeElement("vertical-ham", movieMenu, {innerHTML: "<div></div><div></div><div></div>"})
    verticalHam.addEventListener("click", () => infos.Show(`movie-${this.movieId}`))

    this.BuildQuestionStatus(movie)

    return movie
}

Movie.prototype.BuildPage = function(sequels = [], blockId = "movie") {
    let movie = document.getElementById(blockId)

    let movieImage = MakeElement("movie-image", movie)
    if (this.bannerUrl !== null)
        MakeElement("", movieImage, {src: this.bannerUrl, loading: "lazy"}, "img")
    this.BuildRating(movieImage)

    this.BuildName(movie, "movie-name")

    MakeElement("movie-main-info", movie, {innerText: this.GetMainInfo()})
    MakeElement("movie-sub-info", movie, {innerText: this.GetSubInfo()})

    if (this.shortDescription.text.length > 0)
        MakeElement("movie-short-description", movie, {innerHTML: this.GetSpoileredText(this.shortDescription)})

    if (this.description.text.length > 0) {
        let description = MakeElement("movie-description", movie, {innerHTML: this.GetSpoileredText(this.description)})
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
    this.BuildSequels(movie, sequels)
    this.BuildCites(movie)
    this.BuildAdmin(movie)
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

        if (actor.description.length > 0)
            MakeElement("", actorBlock, {innerText: actor.description})
    }
}

Movie.prototype.BuildPageFacts = function(parent) {
    if (this.facts.length == 0)
        return

    MakeElement("movie-header", parent, {innerText: "Факты"})

    let facts = MakeElement("movie-facts", parent)

    for (let fact of this.facts)
        MakeElement("movie-fact", facts, {innerHTML: this.GetSpoileredText(fact)})
}

Movie.prototype.BuildSequels = function(parent, sequels) {
    if (sequels.length === 0)
        return

    MakeElement("movie-header", parent, {innerText: "Сиквелы и приквелы"})
    let block = MakeElement("movie-sequels", parent)

    for (let sequel of sequels) {
        sequel = new Movie(sequel, this.params)
        block.appendChild(sequel.Build())
        infos.Add(sequel.BuildInfo())
    }
}

Movie.prototype.BuildCites = function(parent) {
    if (this.params.cites.length === 0)
        return

    MakeElement("movie-header", parent, {innerText: "Цитаты"})
    let cites = MakeElement("movie-cites", parent)

    for (let cite of this.params.cites)
        MakeElement("movie-cite", cites, {innerHTML: this.GetSpoileredText(cite.text)})
}

Movie.prototype.BuildInfo = function() {
    let info = MakeElement("info", null, {"id": `info-movie-${this.movieId}`})
    let closeIcon = MakeElement("close-icon", info, {title: "Закрыть"})

    if (this.bannerUrl !== null) {
        let infoImage = MakeElement("info-image", info)
        MakeElement("", infoImage, {src: this.bannerUrl, loading: "lazy"}, "img")
    }

    this.BuildName(info, "info-header-line")

    let rating = MakeElement("info-line", info, {innerHTML: `<b>Рейтинг КП</b>: `})
    MakeElement("info-line", info, {innerHTML: `<b>Тип КМС</b>: ${this.movieType.ToRus()}`})
    MakeElement("info-line", info, {innerHTML: `<b>Год выхода</b>: ${this.year}`})
    this.BuildRating(rating)

    if (this.slogan.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Слоган</b>: ${this.slogan}`})

    if (this.description.text.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Описание</b>: ${this.GetSpoileredText(this.description)}`})

    if (this.shortDescription.text.length > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Короткое описание</b>: ${this.GetSpoileredText(this.shortDescription)}`})

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

Movie.prototype.BuildScale = function(parent) {
    if (!this.params.movieId2scale || !(this.movieId in this.params.movieId2scale))
        return

    let scale = this.params.movieId2scale[this.movieId]
    let circle = MakeElement("circle", parent, {style: `background-color: hsl(${scale.scale * 120}, 70%, 50%)`})
    let correct = GetWordForm(scale.correct, ['корректный', 'корректных', 'корректных'])
    let incorrect = GetWordForm(scale.incorrect, ['некорректный', 'некорректных', 'некорректных'])
    circle.addEventListener("click", () => ShowNotification(`<b>${this.name}</b>: ${correct} и ${incorrect}`, 'info-notification', 3000))
}

Movie.prototype.BuildName = function(parent, className) {
    let header = MakeElement(className, parent)

    this.BuildScale(header)
    let span = MakeElement("", header, {innerText: `${this.name} `}, "span")

    if (this.source.name == "kinopoisk") {
        let link = MakeElement("", header, {href: `https://kinopoisk.ru/film/${this.source.kinopoisk_id}`, target: "_blank"}, "a")
        MakeElement("", link, {src: "/images/kinopoisk.svg"}, "img")
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
        MakeElement("", infoImage, {innerText: actor.description})
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

    let removeButton = MakeElement("basic-button red-button", adminBlock, {innerText: `Удалить ${this.movieType.ToRus()}`}, "button")
    buttons.push(removeButton)
    removeButton.addEventListener("click", () => this.Remove(buttons))
}

Movie.prototype.BuildRating = function(parent) {
    let color = this.GetRatingColor(this.rating.rating_kp)
    let rating = Math.round(this.rating.rating_kp * 10)

    MakeElement("movie-rating", parent, {innerText: `${Math.floor(rating / 10)}.${rating % 10}`, style: `background-color: ${color}`})
}

Movie.prototype.BuildQuestionStatus = function(parent) {
    if (!this.params.movieId2status || !(this.movieId in this.params.movieId2status))
        return

    let status = this.params.movieId2status[this.movieId]
    let correct = status.reduce((sum, value) => sum + value, 0)
    let scale = correct * 100 / status.length
    let color = `hsl(${scale * 1.2}, 70%, 50%)`
    let text = `${GetWordForm(correct, ['игрок', 'игрока', 'игроков'])} из ${status.length}`
    let html = `<b>средний балл</b>: <div class="circle" style="background-color: ${color};"></div>${Round(scale, 10)}% (${text})`

    MakeElement("question-status", parent, {innerHTML: html})

    if (!this.params.movieId2correct || !(this.movieId in this.params.movieId2correct))
        return

    if (this.params.movieId2correct[this.movieId])
        parent.classList.add("movie-correct")
    else
        parent.classList.add("movie-incorrect")
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
    if (rating > 7)
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

    if (hours == 0)
        return `${duration} мин.`

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

Movie.prototype.GetSpoileredText = function(text) {
    let spoilered = []
    let start = 0

    for (let span of text.spoilers) {
        spoilered.push(text.text.slice(start, span[0]))
        spoilered.push(`<span class="spoiler">${text.text.slice(span[0], span[1])}</span>`)
        start = span[1]
    }

    spoilered.push(text.text.slice(start))
    return spoilered.join("").replace(/\n/g, "<br>")
}

Movie.prototype.GetFirstLetter = function() {
    return this.name.replace(/[^a-zа-яё\d]/gi, "")[0].toUpperCase()
}

Movie.prototype.GetNameLength = function() {
    return this.name.toLowerCase().match(/[a-zа-яё\d]/gi).length
}

Movie.prototype.GetMiraclesFieldLetter = function() {
    let letter2count = {}
    let maxCount = 0
    let maxLetter = ""

    for (letter of this.name.toUpperCase()) {
        if (!letter.match(/[a-zа-яё\d]/gi))
            continue

        if (letter in letter2count)
            letter2count[letter] += 1
        else
            letter2count[letter] = 1

        if (letter2count[letter] > maxCount) {
            maxCount = letter2count[letter]
            maxLetter = letter
        }
    }

    return maxLetter
}

Movie.prototype.Remove = function(buttons) {
    if (!confirm(`Вы уверены, что хотите удалить ${this.movieType.ToRus()} "${this.name}"?`))
        return

    for (let button of buttons)
        button.setAttribute("disabled", "")

    SendRequest("/remove-movie", {movie_id: this.movieId}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            for (let button of buttons)
                button.removeAttribute("disabled")

            ShowNotification(`Не удалось удалить ${this.movieType.ToRus()} "${this.name}".<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            return
        }

        location.reload()
    })
}
