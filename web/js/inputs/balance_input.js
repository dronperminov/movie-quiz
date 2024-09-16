function BalanceInput(blockId, errorMessage, value, onChange = null) {
    this.block = document.getElementById(blockId)
    this.error = document.getElementById(`${blockId}-error`)
    this.errorMessage = errorMessage
    this.onChange = onChange

    this.modeCheckbox = document.getElementById(`${blockId}-mode`)
    this.modeCheckbox.addEventListener("change", () => this.SwitchMode(true))
    this.balanceBlock = this.block.getElementsByClassName("balance-input-balance-mode")[0]
    this.checkboxBlock = this.block.getElementsByClassName("balance-input-checkbox-mode")[0]

    this.options = {}
    for (let track of this.block.getElementsByClassName("balance-input-option-track")) {
        let input = track.getElementsByTagName("input")[0]
        let name = input.getAttribute("data-name")
        let id = input.getAttribute("id")
        let value = document.getElementById(`${id}-value`)
        let checkbox = document.getElementById(`${id}-checkbox`)

        this.options[name] = {input, value, checkbox}

        input.addEventListener("input", () => this.UpdateValue(name))
        checkbox.addEventListener("change", () => this.UpdateCheckbox(name))

        if (onChange !== null) {
            input.addEventListener("change", () => onChange())
            checkbox.addEventListener("change", () => onChange())
        }
    }

    this.SetValue(value)
}

BalanceInput.prototype.SetValue = function(value) {
    this.error.innerText = ""

    for (let option of Object.values(this.options)) {
        option.input.value = 50
        option.value.innerText = "50"
        option.checkbox.checked = true
    }

    if (value === null)
        return

    let maxValue = 0
    let minValue = Infinity
    let values = new Set()

    for (let optionValue of Object.values(value)) {
        maxValue = Math.max(maxValue, optionValue)
        minValue = Math.min(minValue, optionValue)
        values.add(optionValue)
    }

    this.modeCheckbox.checked = values.size > 2 || values.size == 2 && minValue > 0

    if (maxValue == 0) {
        maxValue = 1
    }
    else if (minValue == maxValue)
        maxValue *= 2

    for (let [name, option] of Object.entries(this.options)) {
        let optionValue = name in value ? Math.round(value[name] / maxValue * 1000) / 10 : 0
        option.input.value = optionValue
        option.value.innerText = `${optionValue}`
        option.checkbox.checked = optionValue > 0
    }

    this.SwitchMode()
}

BalanceInput.prototype.GetValue = function() {
    let value = {}
    let sum = 0

    for (let [name, option] of Object.entries(this.options)) {
        let optionValue = +option.input.value
        value[name] = optionValue
        sum += optionValue
    }

    if (sum == 0) {
        this.error.innerText = this.errorMessage
        this.block.scrollIntoView({behavior: 'smooth'})
        return null
    }

    for (let [name, nameValue] of Object.entries(value))
        value[name] = nameValue / sum

    return value
}

BalanceInput.prototype.Clear = function() {
    this.SetValue(null)
}

BalanceInput.prototype.UpdateValue = function(name) {
    this.options[name].value.innerText = this.options[name].input.value
    this.options[name].checkbox.checked = +this.options[name].input.value > 0
    this.error.innerText = ""
}

BalanceInput.prototype.UpdateCheckbox = function(name) {
    let value = this.options[name].checkbox.checked ? 50 : 0
    let changed = value != this.options[name].input.value
    this.options[name].input.value = value
    this.options[name].value.innerText = this.options[name].input.value
    this.error.innerText = ""
    return changed
}

BalanceInput.prototype.SwitchMode = function(withChange = false) {
    let balanceMode = this.modeCheckbox.checked
    let changed = false

    if (balanceMode) {
        this.balanceBlock.classList.remove("hidden")
        this.checkboxBlock.classList.add("hidden")
    }
    else {
        this.balanceBlock.classList.add("hidden")
        this.checkboxBlock.classList.remove("hidden")

        for (let name of Object.keys(this.options))
            changed |= this.UpdateCheckbox(name)
    }

    if (withChange && changed)
        this.onChange()
}
