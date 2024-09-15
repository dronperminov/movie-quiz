function GetChildBlock(block, className) {
    let children = block.getElementsByClassName(className)

    while (children.length === 0) {
        block = block.parentNode
        children = block.getElementsByClassName(className)
    }

    return children[0]
}

function InputError(inputId, errorMessage = "") {
    let input = document.getElementById(inputId)
    let label = document.getElementById(`${inputId}-label`)
    let icon = document.getElementById(`${inputId}-icon`)

    let error = GetChildBlock(input, "error")
    error.innerText = errorMessage

    if (errorMessage !== "") {
        input.classList.add("error-input")
        input.focus()

        if (icon !== null)
            icon.classList.add("error-icon")

        if (label !== null)
            label.classList.add("error-label")
    }
    else {
        input.classList.remove("error-input")

        if (icon !== null)
            icon.classList.remove("error-icon")

        if (label !== null)
            label.classList.remove("error-label")
    }
}

function GetTextInput(inputId, errorMessage = "") {
    let input = document.getElementById(inputId)
    let value = input.value.trim()
    input.value = value

    if (value === "" && errorMessage != "") {
        InputError(inputId, errorMessage)
        return null
    }

    InputError(inputId, "")
    return value
}
