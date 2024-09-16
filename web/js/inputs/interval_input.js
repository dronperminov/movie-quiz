function IntervalInput(blockId, prettify = true, value = null, onChange = null) {
    this.block = document.getElementById(blockId)
    this.error = document.getElementById(`${blockId}-error`)
    this.scale2number = {"": 1, "K": 1000, "M": 1000000}
    this.prettify = prettify

    let inputs = this.block.getElementsByTagName("input")
    this.minInput = inputs[0]
    this.maxInput = inputs[1]

    for (let input of inputs) {
        input.addEventListener("input", () => this.ClearErrorInput(input))

        if (onChange !== null)
            input.addEventListener("change", () => onChange())
    }

    this.SetValue(value)
}

IntervalInput.prototype.ClearErrorInput = function(input) {
    input.parentNode.classList.remove("error-input")
    this.error.innerText = ""
}

IntervalInput.prototype.GetInputValue = function(input, message) {
    let value = input.value
    let min = input.hasAttribute("data-min") ? +input.getAttribute("data-min") : -Infinity
    let max = input.hasAttribute("data-max") ? +input.getAttribute("data-max") : Infinity

    if (value === "")
        return ""

    if (value.match(/^\d+(\.\d*)?$/) !== null) {
        value = Math.max(min, Math.min(max, +value))
        input.value = this.PrettifyInputValue(value.toString())
        return value
    }

    let match = (/^(?<number>\d+(\.\d*)?)(?<scale>[kKкКmMмМ])$/).exec(value)
    if (match !== null) {
        let number = +match.groups.number
        let scale = match.groups.scale.replace(/[кk]/gi, "K").replace(/[мm]/gi, "M")

        if (number < 1) {
            number *= 1000
            scale = scale == "K" ? "" : "K"
        }

        value = Math.max(min, Math.min(max, number * this.scale2number[scale]))
        input.value = this.PrettifyInputValue(value.toString())
        return value
    }

    input.focus()
    input.parentNode.classList.add("error-input")

    throw new Error(message)
}

IntervalInput.prototype.PrettifyInputValue = function(value) {
    if (!this.prettify)
        return value

    if (value.match(/^\d+[kKкКmMмМ]$/g))
        return value

    if (value.match(/^\d+000000$/g))
        return `${value.substr(0, value.length - 6)}M`

    if (value.match(/^\d+\d00000$/g))
        return `${value.substr(0, value.length - 6)}.${value.substr(value.length - 6, 1)}M`

    if (value.match(/^\d+000$/g))
        return `${value.substr(0, value.length - 3)}K`

    if (value.match(/^\d+\d00$/g))
        return `${value.substr(0, value.length - 3)}.${value.substr(value.length - 3, 1)}K`

    return value
}

IntervalInput.prototype.SwapValues = function(min, max) {
    if (min === "" || max === "" || min <= max)
        return [min, max]

    let value = this.minInput.value
    this.minInput.value = this.maxInput.value
    this.maxInput.value = value
    return [max, min]
}

IntervalInput.prototype.GetValue = function() {
    this.ClearErrorInput(this.minInput)
    this.ClearErrorInput(this.maxInput)

    try {
        let min = this.GetInputValue(this.minInput, "Начальное значение задано некорректно")
        let max = this.GetInputValue(this.maxInput, "Конечное значение задано некорректно")

        return this.SwapValues(min, max)
    }
    catch (error) {
        this.error.innerText = error.message
        this.block.scrollIntoView({behavior: 'smooth'})
        return null
    }
}

IntervalInput.prototype.SetValue = function(value) {
    if (value === null)
        return

    this.ClearErrorInput(this.minInput)
    this.ClearErrorInput(this.maxInput)
    this.minInput.value = this.PrettifyInputValue(value[0].toString())
    this.maxInput.value = this.PrettifyInputValue(value[1].toString())
}

IntervalInput.prototype.Clear = function() {
    this.minInput.value = ""
    this.maxInput.value = ""
}
