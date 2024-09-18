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

    return {
        query: document.getElementById("query").value.trim(),
        order: document.getElementById("order").value,
        order_type: +document.getElementById("order-type").value,
        movie_type: movieTypeInput.GetValue(),
        production: productionInput.GetValue(),
        years: years,
        votes: votes,
        rating: rating
    }
}

function LoadMovies(response, block) {
    for (let movie of response.movies) {
        movie = new Movie(movie, {personId2person: response.person_id2person, movieId2scale: response.movie_id2scale})
        block.appendChild(movie.Build(response.movie_id2scale))
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

        for (let key of ["order", "order_type"])
            url.searchParams.set(key, params[key])

        for (let key of ["years"])
            if (params[key][0] !== "" || params[key][1] !== "")
                url.searchParams.set(key, JSON.stringify(params[key]))

        for (let key of ["movie_type", "production", "votes", "rating"])
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

    queryInput.value = ""
    orderInput.value = order
    orderTypeInput.value = orderType

    movieTypeInput.Clear()
    productionInput.Clear()
    yearsInput.Clear()
    votesInput.Clear()
    ratingInput.Clear()

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

        let limitInput = new NumberInput("history-limit", 1, Infinity, /^\d+$/g)
        let limit = limitInput.GetValue()
        if (limit === null)
            return

        let skipInput = new NumberInput("history-skip", 0, Infinity, /^\d+$/g)
        let skip = skipInput.GetValue()
        if (skip === null)
            return

        ShowHistory("/history", {actions: [...movieActions, ...personActions], limit: limit, skip: skip})
    })

    return info
}
