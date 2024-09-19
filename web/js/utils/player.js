function Player(trackId, audio, config) {
    this.audio = audio

    this.Build(trackId, config)
    this.InitEvents()
    this.InitMediaSessionHandlers()
    this.InitAudioParams()

    setInterval(() => this.UpdateLoop(), 10)
}

Player.prototype.Build = function(trackId, config) {
    this.block = document.getElementById(`player-${trackId}`)

    this.loadIcon = document.getElementById(`player-${trackId}-load`)
    this.playIcon = document.getElementById(`player-${trackId}-play`)
    this.pauseIcon = document.getElementById(`player-${trackId}-pause`)

    this.icons = this.BuildElement(`player-icons${config.withIcons ? "" : " hidden"}`, this.block)
    this.lyricsIcon = this.BuildElement("player-icon hidden", this.icons, PLAYER_LYRICS_ICON)

    this.progress = this.BuildElement("player-progress", this.block)
    this.progressBar = this.BuildElement("player-progress-bar", this.progress)
    this.progressCurrent = this.BuildElement("player-progress-current", this.progressBar)
    this.time = this.BuildElement("player-time", this.block)

    this.BuildVolume()

    this.lyricsUpdater = null

    if (document.getElementById(`lyrics-updater-${trackId}`) !== null) {
        this.lyricsUpdater = new LyricsUpdater(`lyrics-updater-${trackId}`, (seek) => this.Seek(seek))
        this.lyricsIcon.classList.remove("hidden")

        if (this.lyricsUpdater.IsOpen())
            this.lyricsIcon.classList.add("player-icon-pressed")
        else
            this.lyricsIcon.classList.remove("player-icon-pressed")
    }
}

Player.prototype.InitEvents = function() {
    this.audio.addEventListener("pause", () => this.PauseEvent())
    this.audio.addEventListener("play", () => this.PlayEvent())
    this.audio.addEventListener("seeking", () => this.UpdateProgressBar())

    this.playIcon.addEventListener("click", () => this.Play())
    this.pauseIcon.addEventListener("click", () => this.Pause())
    this.lyricsIcon.addEventListener("click", () => this.ToggleLyrics())

    this.progress.addEventListener("touchstart", (e) => this.ProgressMouseDown(this.PointToSeek(e)))
    this.progress.addEventListener("touchmove", (e) => this.ProgressMouseMove(this.PointToSeek(e)))
    this.progress.addEventListener("touchend", (e) => this.ProgressMouseUp())
    this.progress.addEventListener("touchleave", (e) => this.ProgressMouseUp())

    this.progress.addEventListener("mousedown", (e) => this.ProgressMouseDown(this.PointToSeek(e)))
    this.progress.addEventListener("mousemove", (e) => this.ProgressMouseMove(this.PointToSeek(e)))
    this.progress.addEventListener("mouseup", (e) => this.ProgressMouseUp())
    this.progress.addEventListener("mouseleave", (e) => this.ProgressMouseUp())

    this.volumeInput.addEventListener("touchstart", (e) => this.VolumeMouseDown(this.PointToVolume(e)))
    this.volumeInput.addEventListener("touchmove", (e) => this.VolumeMouseMove(this.PointToVolume(e)))
    this.volumeInput.addEventListener("touchend", (e) => this.VolumeMouseUp())
    this.volumeInput.addEventListener("touchleave", (e) => this.VolumeMouseUp())

    this.volumeInput.addEventListener("mousedown", (e) => this.VolumeMouseDown(this.PointToVolume(e)))
    this.volumeInput.addEventListener("mousemove", (e) => this.VolumeMouseMove(this.PointToVolume(e)))
    this.volumeInput.addEventListener("mouseup", (e) => this.VolumeMouseUp())
    this.volumeInput.addEventListener("mouseleave", (e) => this.VolumeMouseUp())
}

Player.prototype.InitMediaSessionHandlers = function() {
    if (!("mediaSession" in navigator))
        return

    navigator.mediaSession.setActionHandler("seekto", details => this.Seek(this.startTime + details.seekTime))
}

Player.prototype.InitAudioParams = function() {
    let seek = this.audio.hasAttribute("data-seek") ? +this.audio.getAttribute("data-seek") : 0
    let timecode = this.audio.hasAttribute("data-timecode") ? this.audio.getAttribute("data-timecode") : ""
    let playbackRate = this.audio.hasAttribute("data-playback-rate") ? +this.audio.getAttribute("data-playback-rate") : 1

    this.SetTimecode(timecode)
    this.SetPlaybackRate(playbackRate)
    this.Seek(seek)
}

Player.prototype.BuildElement = function(className, parent, innerHTML = "") {
    let element = document.createElement("div")
    element.className = className

    if (innerHTML !== "")
        element.innerHTML = innerHTML

    parent.appendChild(element)
    return element
}

Player.prototype.BuildVolume = function() {
    this.volume = this.BuildElement("player-volume", this.block)
    this.volumeIcon = this.BuildElement("player-icon", this.volume, PLAYER_VOLUME_ICON)
    this.volumeInput = this.BuildElement("player-volume-input hidden", this.volume)
    this.volumeInputBar = this.BuildElement("player-volume-input-bar", this.volumeInput)
    this.volumeInputCurrent = this.BuildElement("player-volume-input-current", this.volumeInputBar)

    this.volumeIcon.addEventListener("click", () => {
        this.volumeInput.classList.toggle("hidden")
        this.volumeIcon.classList.toggle("player-icon-pressed")
    })

    this.SetVolume(localStorage.getItem("player-volume"))
}

Player.prototype.UpdateLoop = function() {
    if (!this.audio.paused)
        this.UpdateProgressBar()
}

Player.prototype.TimeToString = function(time) {
    let seconds = `${Math.floor(time) % 60}`.padStart(2, '0')
    let minutes = `${Math.floor(time / 60)}`.padStart(2, '0')
    return `${minutes}:${seconds}`
}

Player.prototype.Play = function() {
    return this.audio.play()
}

Player.prototype.Pause = function() {
    return this.audio.pause()
}

Player.prototype.Seek = function(seek) {
    this.audio.currentTime = Math.max(this.startTime, Math.min(this.endTime, seek))
}

Player.prototype.SetVolume = function(volume) {
    volume = volume === null ? 100 : Math.max(0, Math.min(100, volume))
    this.volumeInputCurrent.style.height = `${volume}%`
    this.audio.volume = volume / 100
    localStorage.setItem("player-volume", volume)
}

Player.prototype.SetTimecode = function(timecode = "") {
    [this.startTime, this.endTime] = this.ParseTimecode(timecode)
    this.UpdateProgressBar()
}

Player.prototype.SetPlaybackRate = function(playbackRate) {
    this.audio.playbackRate = Math.max(0.25, Math.min(4, playbackRate))
}

Player.prototype.ToggleLyrics = function() {
    if (this.lyricsUpdater === null)
        return

    this.lyricsIcon.classList.toggle("player-icon-pressed")

    if (this.lyricsIcon.classList.contains("player-icon-pressed"))
        this.lyricsUpdater.Open()
    else
        this.lyricsUpdater.Close()
}

Player.prototype.ShowIcons = function() {
    this.icons.classList.remove("hidden")
}

Player.prototype.ParseTimecode = function(timecode) {
    if (timecode === "")
        return [0, this.audio.duration]

    let timestamps = timecode.split(",")

    if (timestamps.length == 1)
        return [+timecode, this.audio.duration]

    return [+timestamps[0], +timestamps[1]]
}

Player.prototype.Reset = function() {
    this.SetTimecode("")
    this.SetPlaybackRate(1)
    this.ShowIcons()
}

Player.prototype.PointToSeek = function(e) {
    let x = e.touches ? e.touches[0].clientX - this.progress.offsetLeft : e.offsetX
    let part = Math.max(0, Math.min(1, x / this.progressBar.clientWidth))
    return this.startTime + part * (this.endTime - this.startTime)
}

Player.prototype.PointToVolume = function(e) {
    e.preventDefault()

    let y

    if (!e.touches) {
        y = e.offsetY
    }
    else {
        let top = 0
        let element = this.volumeInput

        do {
            top += element.offsetTop || 0
            element = element.offsetParent
        }
        while (element)

        y = e.touches[0].clientY - top
    }

    return Math.max(0, Math.min(1, 1 - y / this.volumeInput.clientHeight)) * 100
}

Player.prototype.UpdateProgressBar = function() {
    if (this.audio.currentTime >= this.endTime || this.audio.ended)
        this.audio.currentTime = this.startTime

    let currentTime = Math.max(this.audio.currentTime - this.startTime, 0)
    let duration = Math.max(this.endTime - this.startTime, 0.01)

    if (this.lyricsUpdater !== null)
        this.lyricsUpdater.Update(this.audio.currentTime)

    this.progressCurrent.style.width = `${currentTime / duration * 100}%`
    this.time.innerText = `${this.TimeToString(currentTime)} / ${this.TimeToString(duration)}`

    if ("mediaSession" in navigator)
        navigator.mediaSession.setPositionState({duration: duration, playbackRate: this.audio.playbackRate, position: currentTime})
}

Player.prototype.ProgressMouseDown = function(seek) {
    this.paused = this.audio.paused
    this.pressed = true

    this.Seek(seek)
    this.audio.pause()
}

Player.prototype.ProgressMouseMove = function(seek) {
    if (this.pressed)
        this.Seek(seek)
}

Player.prototype.ProgressMouseUp = function() {
    if (!this.pressed)
        return

    this.pressed = false

    if (!this.paused)
        this.audio.play()
}

Player.prototype.VolumeMouseDown = function(volume) {
    this.pressed = true
    this.SetVolume(volume)
}

Player.prototype.VolumeMouseMove = function(volume) {
    if (this.pressed)
        this.SetVolume(volume)
}

Player.prototype.VolumeMouseUp = function() {
    if (!this.pressed)
        return

    this.pressed = false
}

Player.prototype.PlayEvent = function() {
    this.playIcon.classList.add("hidden")
    this.pauseIcon.classList.remove("hidden")
    this.loadIcon.classList.add("hidden")

    if ("mediaSession" in navigator)
        navigator.mediaSession.playbackState = "playing"
}

Player.prototype.PauseEvent = function() {
    this.playIcon.classList.remove("hidden")
    this.pauseIcon.classList.add("hidden")
    this.loadIcon.classList.add("hidden")

    if ("mediaSession" in navigator)
        navigator.mediaSession.playbackState = "paused"
}
