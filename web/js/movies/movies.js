function GetSearchParams() {
    let years = yearsInput.GetValue()
    if (years === null)
        return null

    let votes = votesInput.GetValue()
    if (votes === null)
        return null

    let rating = ratingInput.GetValue()
    if (rating === null)
        return null

    let ratingImdb = ratingImdbInput.GetValue()
    if (ratingInput === null)
        return null

    return {
        query: document.getElementById("query").value.trim(),
        order: document.getElementById("order").value,
        order_type: +document.getElementById("order-type").value,
        movie_type: movieTypeInput.GetValue(),
        production: productionInput.GetValue(),
        genre: genreInput.GetValue(),
        years: years,
        votes: votes,
        rating: rating,
        rating_imdb: ratingImdb,
        tracks: document.getElementById("tracks").value
    }
}

function LoadMovies(response, block) {
    for (let movie of response.movies) {
        let params = {
            personId2person: response.person_id2person,
            movieId2scale: response.movie_id2scale,
            movieId2correct: response.movie_id2correct ? response.movie_id2correct : null,
            movieId2status: response.movie_id2status ? response.movie_id2status : null
        }

        movie = new Movie(movie, params)
        block.appendChild(movie.Build())
        infos.Add(movie.BuildInfo())
    }

    return response.movies.length
}

function PushUrlParams(params = null) {
    let url = new URL(window.location.href)

    let keys = []
    for (let [key, value] of url.searchParams.entries())
        keys.push(key)

    for (let key of keys)
        url.searchParams.delete(key)

    if (params !== null) {
        if (params.query !== "")
            url.searchParams.set("query", params.query)

        for (let key of ["order", "order_type", "tracks"])
            url.searchParams.set(key, params[key])

        for (let key of ["years"])
            if (params[key][0] !== "" || params[key][1] !== "")
                url.searchParams.set(key, JSON.stringify(params[key]))

        for (let key of ["movie_type", "production", "genre", "votes", "rating", "rating_imdb"])
            if (Object.keys(params[key]).length > 0)
                url.searchParams.set(key, JSON.stringify(params[key]))
    }

    window.history.pushState(null, '', url.toString())
}

function SearchMovies() {
    let params = GetSearchParams()
    if (params === null)
        return

    for (let shortMovies of document.getElementsByClassName("short-movies-block"))
        shortMovies.classList.add("hidden")

    PushUrlParams(params)

    search.CloseFiltersPopup()
    infiniteScroll.Reset()
    infiniteScroll.LoadContent()
}

function ClearMovies() {
    infiniteScroll.Reset()
    PushUrlParams()

    for (let shortMovies of document.getElementsByClassName("short-movies-block"))
        shortMovies.classList.remove("hidden")
}

function SearchShortMovies(order, orderType) {
    let queryInput = document.getElementById("query")
    let orderInput = document.getElementById("order")
    let orderTypeInput = document.getElementById("order-type")
    let tracksInput = document.getElementById("tracks")

    queryInput.value = ""
    orderInput.value = order
    orderTypeInput.value = orderType
    tracksInput.value = "any"

    movieTypeInput.Clear()
    productionInput.Clear()
    genreInput.Clear()
    yearsInput.Clear()
    votesInput.Clear()
    ratingInput.Clear()
    ratingImdbInput.Clear()

    SearchMovies()
}

function BuildAdminInfo() {
    let info = MakeElement("info", null, {id: "info-admin"})

    MakeElement("close-icon", info, {title: "Закрыть"})
    MakeElement("info-header-line", info, {innerText: "Управление"})

    let movieBlock = MakeElement("info-line", info, {innerHTML: "<b>Фильмы</b>"})
    MakeElement("description", movieBlock, {innerText: "Добавление новых и обновление имеющихся фильмов"})

    let movieUrlBlock = MakeElement("info-textarea-line", info)
    let movieUrlLabel = MakeElement("", movieUrlBlock, {innerText: "Ссылки:", "for": "movie-url"}, "label")
    let movieUrlInput = MakeElement("basic-textarea", movieUrlBlock, {type: "text", value: "", placeholder: "https://kinopoisk.ru/film/...", id: "movie-url"}, "textarea")
    MakeElement("error", info, {id: "movie-url-error"})

    let maxImagesBlock = MakeElement("info-input-line", info)
    let maxImagesLabel = MakeElement("", maxImagesBlock, {innerText: "Кадров не более (на фильм):", "for": "movie-max-images"}, "label")
    let maxImagesInput = MakeElement("basic-input", maxImagesBlock, {type: "text", value: "50", id: "movie-max-images"}, "input")
    MakeElement("error", info, {id: "movie-max-images-error"})

    let movieButton = MakeElement("basic-button gradient-button", info, {innerText: "Добавить"}, "button")

    MakeElement("info-divider-line", info)

    let historyBlock = MakeElement("info-line", info, {innerHTML: "<b>История</b>"})
    MakeElement("description", historyBlock, {innerText: "История изменения базы данных"})

    let movieActionsBlock = MakeElement("info-checkbox-line", info)
    let movieActionsInput = MakeCheckbox(movieActionsBlock, "movie-actions", true)
    let movieActionsLabel = MakeElement("", movieActionsBlock, {innerText: "Действия с фильмами", "for": "movie-actions"}, "label")

    let personActionsBlock = MakeElement("info-checkbox-line", info)
    let personActionsInput = MakeCheckbox(personActionsBlock, "person-actions", true)
    let personActionsLabel = MakeElement("", personActionsBlock, {innerText: "Действия с персонами", "for": "person-actions"}, "label")

    let trackActionsBlock = MakeElement("info-checkbox-line", info)
    let trackActionsInput = MakeCheckbox(trackActionsBlock, "track-actions", true)
    let trackActionsLabel = MakeElement("", trackActionsBlock, {innerText: "Действия с треками", "for": "track-actions"}, "label")

    let citeActionsBlock = MakeElement("info-checkbox-line", info)
    let citeActionsInput = MakeCheckbox(citeActionsBlock, "cite-actions", true)
    let citeActionsLabel = MakeElement("", citeActionsBlock, {innerText: "Действия с цитатами", "for": "cite-actions"}, "label")

    let limitBlock = MakeElement("info-input-line", info)
    let limitLabel = MakeElement("", limitBlock, {innerText: "Количество записей:", "for": "history-limit"}, "label")
    let limitInput = MakeElement("basic-input", limitBlock, {type: "text", value: "100", id: "history-limit"}, "input")
    MakeElement("error", info, {id: "history-limit-error"})

    let skipBlock = MakeElement("info-input-line", info)
    let skipLabel = MakeElement("", skipBlock, {innerText: "Смещение:", "for": "history-skip"}, "label")
    let skipInput = MakeElement("basic-input", skipBlock, {type: "text", value: "0", id: "history-skip"}, "input")
    MakeElement("error", info, {id: "history-skip-error"})

    let historyButton = MakeElement("basic-button gradient-button", info, {innerText: "Получить"}, "button")

    movieUrlLabel.addEventListener("click", () => {
        movieUrlInput.value = ""
        movieUrlInput.focus()
    })

    movieButton.addEventListener("click", () => AddMovies([movieButton]))
    historyButton.addEventListener("click", () => {
        let movieActions = movieActionsInput.checked ? ["add_movie", "edit_movie", "remove_movie"] : []
        let personActions = personActionsInput.checked ? ["add_person", "edit_person", "remove_person"] : []
        let trackActions = trackActionsInput.checked ? ["add_track", "edit_track", "remove_track"] : []
        let citeActions = citeActionsInput.checked ? ["add_cite", "edit_cite", "remove_cite"] : []

        let limitInput = new NumberInput("history-limit", 1, Infinity, /^\d+$/g)
        let limit = limitInput.GetValue()
        if (limit === null)
            return

        let skipInput = new NumberInput("history-skip", 0, Infinity, /^\d+$/g)
        let skip = skipInput.GetValue()
        if (skip === null)
            return

        ShowHistory("/history", {actions: [...movieActions, ...personActions, ...trackActions, ...citeActions], limit: limit, skip: skip})
    })

    return info
}
