function LyricsUpdater(blockId, seek, deltaTime = 4000) {
    this.block = document.getElementById(blockId)
    this.block.classList.remove("lyrics-updater-disabled")

    this.deltaTime = deltaTime
    this.wheelTime = null
    this.lrc = this.block.hasAttribute("data-lrc") ? this.block.getAttribute("data-lrc") == "true" : false

    this.InitLines(seek)
    this.InitEvents()
}

LyricsUpdater.prototype.InitLines = function(seek) {
    this.lines = []

    for (let line of this.block.getElementsByClassName("lyrics-line")) {
        let time = +line.getAttribute("data-time")
        this.lines.push({line: line, time: time})

        if (this.lrc)
            line.addEventListener("click", () => seek(time))
    }
}

LyricsUpdater.prototype.InitEvents = function() {
    this.block.addEventListener("wheel", (e) => this.Wheel())
    this.block.addEventListener("resize", (e) => this.Wheel())
    this.block.addEventListener("touchmove", (e) => this.Wheel())
}

LyricsUpdater.prototype.ResetLines = function() {
    for (let line of this.lines)
        line.line.classList.remove("lyrics-line-curr")
}

LyricsUpdater.prototype.Update = function(time) {
    this.ResetLines()

    if (time < this.lines[0].time || !this.lrc)
        return

    let index = 0
    while (index < this.lines.length - 1 && time >= this.lines[index + 1].time)
        index++

    let line = this.lines[index].line
    line.classList.add("lyrics-line-curr")

    if (this.wheelTime === null || performance.now() - this.wheelTime > this.deltaTime) {
        line.parentNode.scrollTo({top: line.offsetTop - line.parentNode.offsetTop - line.parentNode.clientHeight / 2 + line.clientHeight / 2, behavior: "smooth"})
        this.wheelTime = null
    }
}

LyricsUpdater.prototype.Wheel = function() {
    this.wheelTime = performance.now()
}

LyricsUpdater.prototype.Open = function() {
    this.block.classList.remove("hidden")
}

LyricsUpdater.prototype.Close = function() {
    this.block.classList.add("hidden")
}

LyricsUpdater.prototype.IsOpen = function() {
    return !this.block.classList.contains("hidden")
}
