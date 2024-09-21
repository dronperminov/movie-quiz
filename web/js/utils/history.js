function GetActionDiffKeyValue(key, value) {
    if (key == "movie_type")
        return new MovieType(value).ToRus()

    if (key == "genres")
        return value.map(genre => new Genre(genre).ToRus()).join(", ")

    if (key == "production")
        return value.map(production => new Production(production).ToRus()).join(", ")

    return JSON.stringify(value, null, 1).replace("\n", "")
}

function GetActionDiff(action, key, diff) {
    let key2name = {
        "name": {"edit_movie": "название", "edit_person" : "имя"}[action],

        "movie_type": "тип КМС",
        "year": "год выхода",
        "slogan": "слоган",
        "description": "описание",
        "short_description": "короткое описание",
        "production": "производство",
        "countries": "страны",
        "genres": "жанры",
        "actors": "актёры",
        "directors": "продюссеры",
        "duration": "длительность",
        "rating": "рейтинг",
        "image_urls": "кадры",
        "poster_url": "постер",
        "banner_url": "баннер",
        "facts": "факты",
        "cites": "цитаты",
        "tracks": "треки",
        "alternative_names": "альтернативные названия",
        "sequels": "сиквелы/приквелы",

        "photo_url": "фото",

        "downloaded": "скачан",
        "image_url": "изображение"
    }

    let prevValue = `<span class="error-color"><s>${GetActionDiffKeyValue(key, diff.prev)}</s></span>`
    let newValue = `<span class="success-color">${GetActionDiffKeyValue(key, diff.new)}</span>`
    return `<b>${key2name[key]}</b>: ${prevValue} &rarr; ${newValue}`
}

function BuildEditAction(action, parent) {
    let diffBlock = MakeElement("action-diff", parent, {}, "ul")

    for (let [key, diff] of Object.entries(action.diff))
        MakeElement("action-diff-row", diffBlock, {innerHTML: GetActionDiff(action, key, diff)}, "li")
}

function BuildHistory(parent, history) {
    let historyBlock = MakeElement("history", parent)

    let action2title = {
        "edit_movie": "<b>Обновлён</b> фильм",
        "add_movie": '<b class="success-color">Добавлен</b> фильм',
        "remove_movie": '<b class="error-color">Удалён</b> фильм',

        "edit_person": "<b>Обновлена</b> персона",
        "add_person": '<b class="success-color">Добавлена</b> персона',
        "remove_person": '<b class="error-color">Удалена</b> персона',

        "edit_cite": "<b>Обновлена</b> цитата",
        "add_cite": '<b class="success-color">Добавлена</b> цитата',
        "remove_cite": '<b class="error-color">Удалена</b> цитата',

        "edit_track": "<b>Обновлён</b> трек",
        "add_track": '<b class="success-color">Добавлен</b> трек',
        "remove_track": '<b class="error-color">Удалён</b> трек'
    }

    for (let action of history) {
        let actionBlock = MakeElement("action", historyBlock)
        let {date, time} = ParseDateTime(action.timestamp)
        let objectId = ""

        if (action.name == "add_movie")
            objectId = ` <a class="link" href="/movies/${action.movie_id}">${action.movie_id}</a>`
        else if (action.name == "edit_movie")
            objectId = ` <a class="link" href="/movies/${action.movie_id}">${action.movie_id}</a>`
        else if (action.name == "remove_movie")
            objectId = ` ${action.movie_id}`
        else if (action.name == "add_person")
            objectId = ` <a class="link" href="/persons/${action.person_id}">${action.person_id}</a>`
        else if (action.name == "edit_person")
            objectId = ` <a class="link" href="/persons/${action.person_id}">${action.person_id}</a>`
        else if (action.name == "remove_person")
            objectId = ` ${action.person_id}`
        else if (action.name == "add_cite" || action.name == "edit_cite" || action.name == "remove_cite")
            objectId = ` ${action.cite_id}`
        else if (action.name == "add_track" || action.name == "edit_track" || action.name == "remove_track")
            objectId = ` ${action.track_id}`

        MakeElement("action-header", actionBlock, {innerHTML: `${action2title[action.name]}${objectId} @${action.username} ${date} в ${time}`})

        if (action.name.startsWith("edit_")) {
            BuildEditAction(action, actionBlock)
        }
    }
}

function ShowHistory(url, params = null) {
    let info = document.getElementById("info-history")

    if (info === null) {
        info = MakeElement("info", null, {id: "info-history"})

        MakeElement("close-icon", info, {title: "Закрыть"})
        MakeElement("info-header-line", info, {innerText: "История изменений"})
        MakeElement("info-content", info)
        infos.Add(info)
    }

    SendRequest(url, params).then(response => {
        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось получить историю изменений<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            return
        }

        info.children[info.children.length - 1].innerHTML = ""
        BuildHistory(info.children[info.children.length - 1], response.history)
        infos.Show(`history`)
    })
}
