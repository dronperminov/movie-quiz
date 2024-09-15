function SetAttributes(element, attributes) {
    if (attributes === null)
        return

    for (let [name, value] of Object.entries(attributes)) {
        if (name == "innerText")
            element.innerText = value
        else if (name == "innerHTML")
            element.innerHTML = value
        else
            element.setAttribute(name, value)
    }
}

function MakeElement(className, parent = null, attributes = null, tagName = "div") {
    let element = document.createElement(tagName)
    element.className = className

    SetAttributes(element, attributes)

    if (parent !== null)
        parent.appendChild(element)

    return element
}

function MakeCheckbox(parent, id, checked = false) {
    let label = MakeElement("switch-checkbox", parent, {for: id}, "label")
    let input = MakeElement("", label, {type: "checkbox", id: id}, "input")
    let span = MakeElement("switch-checkbox-slider", label, {}, "span")

    if (checked)
        input.setAttribute("checked", "")

    return input
}

function MakeMultiSelect(parent, values, selected) {
    let select = MakeElement("multi-select", parent)

    for (let [name, text] of Object.entries(values)) {
        let option = MakeElement("multi-select-option", select, {"data-name": name, innerText: text})

        if (selected.indexOf(name) > -1)
            option.classList.add("multi-select-option-checked")
    }

    return select
}

function MakeDetails(parent, header, className = "details") {
    let details = MakeElement(className, parent)
    let detailsHeader = MakeElement("details-header", details)
    let detailsIcon = MakeElement("details-icon", detailsHeader, {}, "span")
    let detailsHeaderText = MakeElement("", detailsHeader, {innerText: header}, "span")

    detailsHeader.addEventListener("click", () => details.classList.toggle("details-open"))

    return MakeElement("details-content", details)
}

function GetWordForm(count, forms, onlyForm = false) {
    let index = 0

    if ([0, 5, 6, 7, 8, 9].indexOf(Math.abs(count) % 10) > -1 || [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20].indexOf(Math.abs(count) % 100) > -1)
        index = 2
    else if ([2, 3, 4].indexOf(Math.abs(count) % 10) > -1) 
        index = 1

    return onlyForm ? forms[index] : `${count} ${forms[index]}`
}

function Round(value, scale = 100) {
    return Math.round(value * scale) / scale
}

function FormatTime(time) {
    if (time >= 60) {
        let seconds = `${Math.floor(time) % 60}`.padStart(2, '0')
        let minutes = `${Math.floor(time / 60)}`.padStart(2, '0')
        return `${minutes}:${seconds}`
    }

    if (time >= 10)
        return GetWordForm(Math.round(time), ['секунда', 'секунды', 'секунд'])

    let rounded = Math.round(time * 10)
    let last = rounded % 10
    return `${Round(time, 10)} ${GetWordForm(last == 0 || last == 5 ? Math.floor(rounded / 10) : last, ['секунда', 'секунды', 'секунд'], true)}`
}

function ParseDateTime(datetime) {
    let match = (/^(?<year>\d\d\d\d)-(?<month>\d\d?)-(?<day>\d\d?)T(?<time>\d\d?:\d\d:\d\d?)(\.\d+)?$/g).exec(datetime)
    let groups = match.groups

    return {date: `${groups.day}.${groups.month}.${groups.year}`, time: groups.time}
}

function ClearSearchParams(url) {
    let keys = []

    for (let [key, value] of url.searchParams.entries())
        keys.push(key)

    for (let key of keys)
        url.searchParams.delete(key)
}

function FormatTotalTime(total) {
    if (total < 60)
        return `${Math.round(total * 10) / 10} сек.`

    let seconds = Math.round(total)
    let minutes = `${Math.floor(seconds / 60) % 60}`.padStart(2, '0')
    let hours = Math.floor(seconds / 3600)
    seconds = `${seconds % 60}`.padStart(2, '0')

    if (total < 3600)
        return `${minutes} мин. ${seconds} сек.`

    return `${hours} ч. ${minutes} мин.`
}

function LevenshteinDistance(s, t) {
    if (!s.length)
        return t.length

    if (!t.length)
        return s.length

    let arr = []

    for (let i = 0; i <= t.length; i++) {
        arr[i] = [i]

        for (let j = 1; j <= s.length; j++)
            arr[i][j] = i === 0 ? j : Math.min(arr[i - 1][j] + 1, arr[i][j - 1] + 1, arr[i - 1][j - 1] + (s[j - 1] === t[i - 1] ? 0 : 1))
    }

    return arr[t.length][s.length]
}

function Ratio(s, t) {
    let len = Math.max(s.length, t.length)
    let distance = LevenshteinDistance(s, t)
    return 1 - distance / Math.max(len, 1)
}
