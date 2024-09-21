function Track(data) {
    this.trackId = data.track_id
    this.source = data.source
    this.title = data.title
    this.artists = data.artists
    this.lyrics = data.lyrics
    this.duration = data.duration
    this.imageUrl = data.image_url !== null ? data.image_url : '/images/tracks/default.png'
    this.metadata = new Metadata(data.metadata, "Добавлен", "Обновлён")
    this.downloaded = data.downloaded
}

Track.prototype.Build = function(config = null) {
    let track = MakeElement("track", null, {id: `track-${this.trackId}`})

    if (config === null)
        config = {asUnknown: false, asQuestion: false}

    if (config.asQuestion)
        track.classList.add("track-question")

    if (config.asUnknown)
        track.classList.add("track-unknown")

    this.BuildAudio(track)
    this.BuildMain(track, config.asUnknown)

    MakeElement("player", track, {id: `player-${this.trackId}`})
    this.BuildLyrics(track)

    return track
}

Track.prototype.BuildInfo = function() {
    let info = MakeElement("info")
    info.setAttribute("id", `info-track-${this.trackId}`)

    let closeIcon = MakeElement("close-icon", info, {title: "Закрыть"})

    let infoImage = MakeElement("info-image", info)
    let img = MakeElement("", infoImage, {src: this.imageUrl, loading: "lazy"}, "img")

    this.BuildName(info)

    MakeElement("info-line", info, {innerHTML: `<b>Исполнител${this.artists.length == 1 ? "ь" : "и"}</b>: ${this.artists.join(", ")}`})

    if (this.duration > 0)
        MakeElement("info-line", info, {innerHTML: `<b>Длительность:</b> ${this.FormatDuration()}`})

    this.metadata.BuildInfo(info)
    this.BuildAdmin(info)

    return info
}

Track.prototype.BuildAudio = function(parent) {
    this.audio = MakeElement("", parent, {}, "audio")

    this.audio.setAttribute("id", `audio-${this.trackId}`)
    this.audio.setAttribute("data-track-id", this.trackId)
    this.audio.setAttribute("preload", "metadata")

    if (this.downloaded)
        this.audio.setAttribute("data-src", `https://music.dronperminov.ru/movie_tracks/${this.trackId}.mp3`)
    else
        this.audio.setAttribute("data-yandex-id", this.source.yandex_id)
}

Track.prototype.BuildMain = function(parent, asUnknown) {
    let trackMain = MakeElement("track-main", parent)

    let trackImage = MakeElement("track-image", trackMain)
    let image = MakeElement("", trackImage, {id: "track-image", src: asUnknown ? "/images/tracks/default.png" : this.imageUrl}, "img")
    image.addEventListener("click", () => PlayPauseTrack(this.trackId))

    if (this.lyrics)
        MakeElement("track-image-lyrics", trackImage, {innerText: "T"})

    let div = MakeElement("", trackMain)
    MakeElement("track-title", div, {innerText: asUnknown ? "НЕИЗВЕСТЕН" : this.title})
    MakeElement("track-artists", div, {innerText: asUnknown ? "неизвестный исполнитель" : this.artists.join(", ")})

    this.BuildTrackControls(trackMain)
    this.BuildMenu(trackMain)
}

Track.prototype.BuildTrackControls = function(parent) {
    let controls = MakeElement("track-controls", parent)

    let loader = MakeElement("loader hidden", controls, {"id": `loader-${this.trackId}`})
    MakeElement("", loader, {src: "/images/loader.svg"}, "img")

    let loadIcon = MakeElement("", controls, {innerHTML: TRACK_LOAD_ICON, id: `player-${this.trackId}-load`})
    let playIcon = MakeElement("hidden", controls, {innerHTML: TRACK_PLAY_ICON, id: `player-${this.trackId}-play`})
    let pauseIcon = MakeElement("hidden", controls, {innerHTML: TRACK_PAUSE_ICON, id: `player-${this.trackId}-pause`})

    loadIcon.addEventListener("click", () => PlayTrack(this.trackId))
}

Track.prototype.BuildMenu = function(parent) {
    let trackMenu = MakeElement("track-menu", parent)
    let ham = MakeElement("vertical-ham", trackMenu, {id: "track-menu"})
    ham.addEventListener("click", () => infos.Show(`track-${this.trackId}`))

    MakeElement("", ham)
    MakeElement("", ham)
    MakeElement("", ham)
}

Track.prototype.BuildLyrics = function(parent) {
    if (this.lyrics === null)
        return

    let block = MakeElement("hidden", parent, {id: `lyrics-updater-${this.trackId}`, "data-lrc": this.lyrics.lrc})
    let updater = MakeElement("lyrics-updater", block)
    let lines = MakeElement("lyrics-lines", updater)

    for (let line of this.lyrics.lines)
        MakeElement("lyrics-line", lines, {innerText: line.text, "data-time": line.time})
}

Track.prototype.BuildName = function(parent) {
    let header = MakeElement("info-header-line", parent)

    if (this.source.name == "yandex") {
        let link = MakeElement("", header, {href: `https://music.yandex.ru/track/${this.source.yandex_id}`, target: "_blank"}, "a")
        MakeElement("", link, {src: "/images/ya_music.svg"}, "img")
    }

    MakeElement("", header, {innerText: this.title}, "span")
}

Track.prototype.BuildAdmin = function(block) {
    let adminBlock = MakeElement("admin-buttons admin-block", block)

    let historyButton = MakeElement("basic-button gradient-button", adminBlock, {innerText: "История изменений"}, "button")
    historyButton.addEventListener("click", () => ShowHistory(`/track-history/${this.trackId}`))

    let removeButton = MakeElement("basic-button red-button", adminBlock, {innerText: "Удалить трек"}, "button")
    removeButton.addEventListener("click", () => this.Remove([removeButton]))
}

Track.prototype.FormatDuration = function() {
    let duration = Math.round(this.duration)
    let minutes = `${Math.floor(duration / 60)}`.padStart(2, '0')
    let seconds = `${duration % 60}`.padStart(2, '0')

    return `${minutes}:${seconds}`
}

Track.prototype.Remove = function(buttons) {
    if (!confirm(`Вы уверены, что хотите удалить трек "${this.title}"?`))
        return

    for (let button of buttons)
        button.setAttribute("disabled", "")

    SendRequest("/remove-track", {track_id: this.trackId}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            for (let button of buttons)
                button.removeAttribute("disabled")

            ShowNotification(`Не удалось удалить трек "${this.title}".<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            return
        }

        location.reload()
    })
}