function NumberInput(inputId, min, max, pattern, value = null, onChange = null) {
    this.input = document.getElementById(inputId)
    this.error = document.getElementById(`${inputId}-error`)
    this.input.addEventListener("input", () => this.Input())

    if (onChange !== null)
        this.input.addEventListener("change", () => onChange())

    this.min = min
    this.max = max
    this.pattern = pattern

    this.SetValue(value)
}

NumberInput.prototype.SetValue = function(value) {
    if (value === null)
        return

    this.input.value = value
    this.Input()
}

NumberInput.prototype.GetValue = function() {
    let value = this.input.value

    if (value.match(this.pattern) === null) {
        this.input.classList.add("error-input")
        this.input.focus()
        this.error.innerText = "Введено некорректное число"
        this.input.scrollIntoView({behavior: 'smooth'})
        return null
    }

    if (+value < this.min)
        value = this.min

    if (+value > this.max)
        value = this.max

    this.input.value = value
    return +value
}

NumberInput.prototype.Input = function() {
    this.input.classList.remove("error-input")
    this.error.innerText = ""
}