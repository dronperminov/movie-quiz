function LoadTrack(trackId) {
    let audio = document.getElementById(`audio-${trackId}`)
    let loader = document.getElementById(`loader-${trackId}`)
    let loadIcon = document.getElementById(`player-${trackId}-load`)

    if (audio.hasAttribute("src")) {
        loader.classList.add("hidden")
        return new Promise((resolve, reject) => resolve(true))
    }

    if (audio.hasAttribute("data-src")) {
        loader.classList.add("hidden")

        return new Promise((resolve, reject) => {
            audio.src = audio.getAttribute("data-src")
            resolve(true)
        })
    }

    return SendRequest("/get-direct-link", {yandex_id: audio.getAttribute("data-yandex-id")}).then(response => {
        loader.classList.add("hidden")

        if (response.status != "success") {
            ShowNotification(response.message, "error-notification")
            audio.classList.remove("loaded")
            loadIcon.classList.remove("hidden")
            return false
        }

        audio.src = response.direct_link
        return true
    })
}

function PlayTrack(trackId) {
    let audio = document.getElementById(`audio-${trackId}`)
    let loader = document.getElementById(`loader-${trackId}`)
    let loadIcon = document.getElementById(`player-${trackId}-load`)

    if (audio.classList.contains("loaded"))
        return

    audio.classList.add("loaded")
    loader.classList.remove("hidden")
    loadIcon.classList.add("hidden")

    if (!audio.classList.contains("event-added")) {
        audio.classList.add("event-added")
        audio.addEventListener("loadedmetadata", () => LoadedMetadata(trackId, audio))
        audio.addEventListener("play", () => players.Pause(audio))
    }

    SetMediaSessionMetadata(trackId)
    LoadTrack(trackId)
}

function PlayPauseTrack(trackId) {
    let audio = document.getElementById(`audio-${trackId}`)

    if (!audio.classList.contains("loaded")) {
        PlayTrack(trackId)
    }
    else if (audio.paused) {
        audio.play()
    }
    else {
        audio.pause()
    }
}

function LoadedMetadata(trackId, audio) {
    let player = players.Add(trackId, audio)
    let playResult = player.Play()
    playResult.catch(() => PlayError(trackId))
}

function PlayError(trackId) {
    let playIcon = document.getElementById(`player-${trackId}-play`)
    playIcon.classList.remove("hidden")

    ShowNotification("Не удалось запустить трек, требуется ручное нажатие", "error-notification")
}

function SetMediaSessionMetadata(trackId) {
    let trackBlock = document.getElementById(`track-${trackId}`)
    let title = trackBlock.getElementsByClassName("track-title")[0].innerText
    let artists = trackBlock.getElementsByClassName("track-artists")[0].innerText
    let image = trackBlock.getElementsByClassName("track-image")[0].getElementsByTagName("img")[0]

    if ("mediaSession" in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: title,
            artist: artists,
            artwork: [{src: image.src, sizes: '400x400', type: 'image/png'}]
        })
    }
}
