function Search(blockId = "search", onSearch, onClear) {
    this.block = document.getElementById(blockId)
    this.block.addEventListener("click", (e) => this.ClickBlock(e))

    this.onSearch = onSearch
    this.onClear = onClear

    this.clear = this.block.getElementsByClassName("search-clear")[0]
    this.clear.addEventListener("click", () => this.ClearQuery())

    this.query = this.block.getElementsByClassName("search-query")[0]
    this.queryInput = this.query.children[0]
    this.queryInput.addEventListener("keydown", (e) => this.QueryKeyDown(e))
    this.queryInput.addEventListener("input", (e) => this.QueryInput(e))
    this.queryInput.addEventListener("focus", (e) => this.QueryFocus())
    this.queryInput.addEventListener("focusout", (e) => this.QueryFocusOut())

    this.filters = this.block.getElementsByClassName("search-filters")[0]
    this.filters.addEventListener("click", (e) => this.ToggleFiltersPopup())
    this.filtersPopup = this.block.getElementsByClassName("search-filters-popup")[0]

    new SwipeHandler(this.filtersPopup, () => this.ToggleFiltersPopup(), SWIPE_HANDLER_DOWN)
}

Search.prototype.GetQuery = function() {
    return this.queryInput.value.trim()
}

Search.prototype.ClearQuery = function() {
    this.queryInput.value = ""
    this.block.classList.add("search-query-empty")
    this.onClear()
}

Search.prototype.QueryKeyDown = function(e) {
    if (e.key != "Enter")
        return

    e.preventDefault()
    this.Search()
}

Search.prototype.Search = function() {
    this.block.classList.remove("search-focus")
    this.queryInput.blur()

    this.onSearch()
}

Search.prototype.ClickBlock = function(e) {
    if (this.clear.contains(e.target) || this.filters.contains(e.target) || this.filtersPopup.contains(e.target))
        return

    e.preventDefault()
    this.queryInput.focus()
}

Search.prototype.QueryInput = function(e) {
    let query = this.GetQuery()

    if (query.length == 0) {
        this.block.classList.add("search-query-empty")
    }
    else {
        this.block.classList.remove("search-query-empty")
    }
}

Search.prototype.QueryFocus = function() {
    this.block.classList.add("search-focus")
}

Search.prototype.QueryFocusOut = function() {
    this.queryInput.value = this.GetQuery()
    this.block.classList.remove("search-focus")
}

Search.prototype.CloseFiltersPopup = function() {
    this.filtersPopup.classList.remove("search-filters-popup-open")
    this.filters.classList.remove("search-filters-open")

    let body = document.getElementsByTagName("body")[0]
    body.classList.remove("no-overflow")
}

Search.prototype.ToggleFiltersPopup = function() {
    this.filtersPopup.classList.toggle("search-filters-popup-open")
    this.filters.classList.toggle("search-filters-open")

    let body = document.getElementsByTagName("body")[0]
    body.classList.toggle("no-overflow")
}
