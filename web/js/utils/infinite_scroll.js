const INfINITE_SCROLL_INITIAL_STATUS = "initial"
const INfINITE_SCROLL_LOADING_STATUS = "loading"
const INfINITE_SCROLL_LOADED_STATUS = "loaded"
const INfINITE_SCROLL_OUT_DATA_STATUS = "out-data"
const INfINITE_SCROLL_ERROR_STATUS = "error"

function InfiniteScroll(blockId, config) {
    let block = document.getElementById(blockId)

    this.results = block.children[0]
    this.block = block.children[1]
    this.loader = block.children[2]

    this.pageSize = config.pageSize || 10
    this.offset = config.offset || 100

    this.url = config.url
    this.getParams = config.getParams
    this.onLoad = config.onLoad

    this.Reset()

    window.addEventListener("scroll", e => this.Scroll())
}

InfiniteScroll.prototype.Reset = function() {
    this.page = 0
    this.status = INfINITE_SCROLL_INITIAL_STATUS

    this.block.innerHTML = ""
    this.results.innerHTML = ""
    this.loader.classList.add("hidden")
}

InfiniteScroll.prototype.LoadContent = function() {
    let params = this.getParams()

    if (params === null)
        return

    params.page = this.page
    params.page_size = this.pageSize

    this.status = INfINITE_SCROLL_LOADING_STATUS
    this.loader.classList.remove("hidden")

    SendRequest(this.url, params).then(response => {
        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось загрузить данные<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            this.status = INfINITE_SCROLL_ERROR_STATUS
            setTimeout(() => this.LoadContent(), 3000)
            return
        }

        this.loader.classList.add("hidden")

        if (response.total > 0)
            this.results.innerText = `${GetWordForm(response.total, ['результат нашёлся', 'результата нашлось', 'результатов нашлось'])} по запросу`
        else
            this.results.innerText = "К сожалению, по запросу ничего не нашлось"

        let count = this.onLoad(response, this.block)
        this.status = count == this.pageSize ? INfINITE_SCROLL_LOADED_STATUS : INfINITE_SCROLL_OUT_DATA_STATUS
        this.page += 1
    })
}

InfiniteScroll.prototype.Scroll = function() {
    if (this.status != INfINITE_SCROLL_LOADED_STATUS)
        return

    let end = this.block.offsetTop + this.block.clientHeight
    let scroll = window.innerHeight + window.scrollY

    if (scroll >= end - this.offset)
        this.LoadContent()
}
