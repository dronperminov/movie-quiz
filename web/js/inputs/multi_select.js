function MultiSelect(blockId, value = null, onlyCheck = false, onChange = null) {
    this.block = typeof blockId === "string" ? document.getElementById(blockId) : blockId
    this.options = {}
    this.onlyCheck = onlyCheck
    this.onChange = onChange

    for (let option of this.block.children) {
        option.addEventListener("click", () => this.ClickOption(option))
        this.options[option.getAttribute("data-name")] = option
    }

    this.SetValue(value)
}

MultiSelect.prototype.GetOptionValue = function(option) {
    if (option.classList.contains("multi-select-option-checked"))
        return true

    if (option.classList.contains("multi-select-option-unchecked"))
        return false

    return null
}

MultiSelect.prototype.SetOptionValue = function(option, value) {
    option.classList.remove("multi-select-option-checked")
    option.classList.remove("multi-select-option-unchecked")

    if (value === null)
        return

    if (value)
        option.classList.add("multi-select-option-checked")
    else
        option.classList.add("multi-select-option-unchecked")
}

MultiSelect.prototype.ClickOption = function(option) {
    if (this.onlyCheck) {
        option.classList.toggle("multi-select-option-checked")
    }
    else if (option.classList.contains("multi-select-option-checked")) {
        option.classList.remove("multi-select-option-checked")
        option.classList.add("multi-select-option-unchecked")
    }
    else if (option.classList.contains("multi-select-option-unchecked")) {
        option.classList.remove("multi-select-option-unchecked")
    }
    else {
        option.classList.add("multi-select-option-checked")
    }

    if (this.onChange !== null)
        this.onChange()
}

MultiSelect.prototype.Disable = function() {
    this.block.classList.add("multi-select-disabled")
}

MultiSelect.prototype.Enable = function() {
    this.block.classList.remove("multi-select-disabled")
}

MultiSelect.prototype.GetValue = function() {
    let value = {}

    for (let [name, option] of Object.entries(this.options)) {
        let optionValue = this.GetOptionValue(option)

        if (optionValue !== null)
            value[name] = optionValue
    }

    return value
}

MultiSelect.prototype.SetValue = function(value) {
    if (value === null)
        return

    this.Clear()

    for (let [name, nameValue] of Object.entries(value))
        this.SetOptionValue(this.options[name], nameValue)
}

MultiSelect.prototype.GetSelected = function() {
    let selected = []

    for (let [name, option] of Object.entries(this.options))
        if (this.GetOptionValue(option))
            selected.push(name)

    return selected
}

MultiSelect.prototype.SetSelected = function(selected) {
    this.SetValue({})

    for (let value of selected)
        this.options[value].classList.add("multi-select-option-checked")
}

MultiSelect.prototype.Clear = function() {
    for (let option of Object.values(this.options)) {
        option.classList.remove("multi-select-option-checked")
        option.classList.remove("multi-select-option-unchecked")
    }
}
