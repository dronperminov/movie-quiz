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
        movie = new Movie(movie, {personId2person: response.person_id2person})
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
