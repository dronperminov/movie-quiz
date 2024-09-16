function InfoPanels() {
    this.popup = document.createElement("div")
    this.popup.classList.add("info-popup")
    this.popup.addEventListener("click", () => this.Close())

    this.blocks = document.createElement("div")

    let body = document.getElementsByTagName("body")[0]
    body.appendChild(this.popup)
    body.appendChild(this.blocks)
}

InfoPanels.prototype.Clear = function() {
    this.blocks.innerHTML = ""
}

InfoPanels.prototype.Add = function(block) {
    this.blocks.appendChild(block)

    let handler = new SwipeHandler(block, () => this.Close(), SWIPE_HANDLER_DOWN)

    for (let closeIcon of block.getElementsByClassName("close-icon"))
        closeIcon.addEventListener("click", () => this.Close())

    block.classList.add("info-handled")
}

InfoPanels.prototype.Show = function(infoId) {
    let body = document.getElementsByTagName("body")[0]
    body.classList.add("no-overflow")

    for (let info of document.getElementsByClassName(`info`))
        info.classList.remove("info-open")

    this.popup.classList.add('info-popup-open')

    let info = document.getElementById(`info-${infoId}`)
    info.classList.add('info-open')
    info.scrollTop = 0
}

InfoPanels.prototype.Close = function() {
    let body = document.getElementsByTagName("body")[0]
    body.classList.remove("no-overflow")

    this.popup.classList.remove('info-popup-open')

    for (info of document.getElementsByClassName("info-open"))
        info.classList.remove('info-open')
}
