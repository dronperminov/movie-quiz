function TextInput(inputId, pattern, errorMessage, multiline = false, value = null, onChange = null) {
    this.input = document.getElementById(inputId)
    this.error = document.getElementById(`${inputId}-error`)
    this.input.addEventListener("input", () => this.Input())

    if (onChange !== null)
        this.input.addEventListener("change", () => onChange())

    this.pattern = pattern
    this.errorMessage = errorMessage
    this.multiline = multiline

    this.SetValue(value)
}

TextInput.prototype.SetValue = function(value) {
    if (value === null)
        return

    this.input.value = value
    this.Input()
}

TextInput.prototype.ValidateValue = function(value) {
    if (value.match(this.pattern) === null) {
        this.input.classList.add("error-input")
        this.input.focus()
        this.error.innerText = this.errorMessage
        this.input.scrollIntoView({behavior: 'smooth'})
        return null
    }

    return value
}

TextInput.prototype.GetValue = function() {
    if (!this.multiline) {
        let value = this.input.value.trim()
        this.input.value = value
        return this.ValidateValue(value)
    }

    let lines = this.input.value.split("\n").map(line => line.trim()).filter(line => line.length > 0)

    for (let line of lines) {
        let value = this.ValidateValue(line)

        if (value === null)
            return
    }

    return lines
}

TextInput.prototype.Input = function() {
    this.input.classList.remove("error-input")
    this.error.innerText = ""
}
