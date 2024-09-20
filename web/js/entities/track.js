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

    let div = MakeElement("", trackMain)
    MakeElement("track-title", div, {innerText: asUnknown ? "НЕИЗВЕСТЕН" : this.title})
    MakeElement("track-artists", div, {innerText: asUnknown ? "неизвестный исполнитель" : this.artists.join(", ")})

    this.BuildTrackControls(trackMain)
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

Track.prototype.BuildLyrics = function(parent) {
    if (this.lyrics === null)
        return

    let block = MakeElement("hidden", parent, {id: `lyrics-updater-${this.trackId}`, "data-lrc": this.lyrics.lrc})
    let updater = MakeElement("lyrics-updater", block)
    let lines = MakeElement("lyrics-lines", updater)

    for (let line of this.lyrics.lines)
        MakeElement("lyrics-line", lines, {innerText: line.text, "data-time": line.time})
}
