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
