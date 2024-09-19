function ParseMovies(buttons, movieIds, maxImages = 50) {
    if (movieIds.length == 0)
        return

    for (let button of buttons)
        button.setAttribute("disabled", "")

    SendRequest("/parse-movies", {movie_ids: movieIds, max_images: maxImages}).then(response => {
        for (let button of buttons)
            button.removeAttribute("disabled")

        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось распарсить фильм${movieIds.length == 1 ? "" : "ы"}<br><b>Причина:</b> ${response.message}`, "error-notification")
            return
        }

        let text = GetWordForm(response.movies, ["фильм успешно распаршен", "фильма успешно распаршены", "фильмов успешно распаршены"])
        ShowNotification(`${text} (новые фильмы: ${response.new_movies}, новые персоны: ${response.new_persons}, удалённые персоны: ${response.removed_persons}).`, "success-notification")
    })
}

function ParseMovieTracks(buttons, movieId, trackIds) {
    if (trackIds.length == 0)
        return

    for (let button of buttons)
        button.setAttribute("disabled", "")

    SendRequest("/parse-movie-tracks", {movie_id: movieId, track_ids: trackIds}).then(response => {
        for (let button of buttons)
            button.removeAttribute("disabled")

        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось распарсить трек${trackIds.length == 1 ? "" : "и"}<br><b>Причина:</b> ${response.message}`, "error-notification")
            return
        }

        ShowNotification(GetWordForm(response.tracks, ["трек успешно распаршен", "трека успешно распаршены", "треков успешно распаршены"]), "success-notification")
    })
}

function AddMovies(buttons) {
    let urlRegex = /^https:\/\/(www\.)?kinopoisk\.ru\/(film|series)\/(?<movieId>\d+)/g
    let urlInput = new TextInput("movie-url", urlRegex, "Введена некорректная ссылка", true)
    let urls = urlInput.GetValue()
    if (urls === null)
        return

    let maxImagesInput = new NumberInput("movie-max-images", 1, 100, /^\d+$/g)
    let maxImages = maxImagesInput.GetValue()
    if (maxImages === null)
        return

    let movieIds = Array.from(new Set(urls.map(url => +/(film|series)\/(?<movieId>\d+)/g.exec(url).groups.movieId)))
    ParseMovies(buttons, movieIds, maxImages)
}

function AddTrack(movieId, buttons) {
    let urlRegex = /^https:\/\/music\.yandex\.ru\/(album\/\d+\/)?track\/(?<trackId>\d+)/g
    let urlInput = new TextInput("track-url", urlRegex, "Введена некорректная ссылка", true)
    let urls = urlInput.GetValue()
    if (urls === null)
        return

    let trackIds = Array.from(new Set(urls.map(url => /track\/(?<trackId>\d+)/g.exec(url).groups.trackId)))
    ParseMovieTracks(buttons, movieId, trackIds)
}
