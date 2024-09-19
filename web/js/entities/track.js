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

Track.prototype.Build = function() {
    let track = MakeElement("track", null, {id: `track-${this.trackId}`})

    this.BuildAudio(track)
    this.BuildMain(track)

    MakeElement("player", track, {id: `player-${this.trackId}`})
    this.BuildLyrics(track)

    return track
}

Track.prototype.BuildAudio = function(parent) {
    let audio = MakeElement("", parent, {}, "audio")

    audio.setAttribute("id", `audio-${this.trackId}`)
    audio.setAttribute("data-track-id", this.trackId)
    audio.setAttribute("preload", "metadata")

    if (this.downloaded)
        audio.setAttribute("data-src", `https://music.dronperminov.ru/movie_tracks/${this.trackId}.mp3`)
    else
        audio.setAttribute("data-yandex-id", this.source.yandex_id)
}

Track.prototype.BuildMain = function(parent) {
    let trackMain = MakeElement("track-main", parent)

    let trackImage = MakeElement("track-image", trackMain)
    let image = MakeElement("", trackImage, {id: "track-image", src: this.imageUrl}, "img")
    image.addEventListener("click", () => PlayPauseTrack(this.trackId))

    let div = MakeElement("", trackMain)
    MakeElement("track-title", div, {innerText: this.title})
    MakeElement("track-artists", div, {innerText: this.artists.join(", ")})

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
