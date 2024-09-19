const key2color = {
    total: "#2f7bf0",
    correct: "#47b39c",
    incorrect: "#ec6b56",
    unknown: "#ffc154",

    questions: "#d82e6b",
    time: "#d82e6b"
}

function ToggleQuestionsChart() {
    if (Math.max(...questionsData.map(data => data.value)) == 0)
        return

    let chartBlock = document.getElementById("questions-chart-block")
    chartBlock.classList.toggle("analytics-chart-open")

    if (chartBlock.classList.contains("analytics-chart-open"))
        ShowQuestionsChart()
}

function ShowQuestionsChart() {
    if (Math.max(...questionsData.map(data => data.value)) == 0)
        return

    let chartBlock = document.getElementById("questions-chart-block")
    chartBlock.classList.add("analytics-chart-open")

    let svg = document.getElementById("questions-chart")
    let chart = new Chart()
    chart.Plot(svg, questionsData)

    let block = document.getElementById("questions-block")
    block.scrollIntoView({behavior: "smooth"})
}

function ToggleTotalTimeChart() {
    let block = document.getElementById("total-time-block")
    block.classList.toggle("analytics-chart-open")

    let smallBar = document.getElementById("total-time-small-bar")
    smallBar.classList.toggle("analytics-bar-small")
}

function ToggleTimesChart() {
    if (timesData.total.reduce((sum, value) => sum + value.count, 0) == 0)
        return

    let block = document.getElementById("times-chart-block")
    block.classList.toggle("analytics-chart-open")

    for (let key of ["total", "correct", "incorrect"]) {
        let label = document.getElementById(`times-${key}-label`)
        label.classList.remove("analytics-label-selected")
    }

    if (block.classList.contains("analytics-chart-open"))
        ShowTimesChart("total")
}

function ShowTimesChart(targetKey = null) {
    if (timesData.total.reduce((sum, value) => sum + value.count, 0) == 0)
        return

    let chartBlock = document.getElementById("times-chart-block")
    chartBlock.classList.add("analytics-chart-open")

    let oneScale = document.getElementById("times-scale").checked
    let maxTime = 0

    for (let key of ["total", "correct", "incorrect"]) {
        maxTime = Math.max(maxTime, ...timesData[key].map(data => data.count))

        if (targetKey === null && !document.getElementById(`times-${key}-chart`).classList.contains("hidden"))
            targetKey = key
    }

    for (let key of ["total", "correct", "incorrect"]) {
        let svg = document.getElementById(`times-${key}-chart`)
        let label = document.getElementById(`times-${key}-label`)

        if (key != targetKey) {
            svg.classList.add("hidden")
            label.classList.remove("analytics-label-selected")
            continue
        }

        svg.classList.remove("hidden")
        label.classList.add("analytics-label-selected")

        let chart = new BarChart({barColor: key2color[key], minRectWidth: 32, maxRectWidth: 45, bottomPadding: 12})
        chart.Plot(svg, timesData[key], "label", "count", oneScale ? maxTime : null)
    }

    let block = document.getElementById("times-block")
    block.scrollIntoView({behavior: "smooth"})
}

function PlotPeriodBarChart(key, maxValue = null) {
    let svg = document.getElementById(`period-${key}-chart`)

    if (svg === null)
        return

    let chart = new BarChart({barColor: key2color[key], minRectWidth: 32, maxRectWidth: 38, bottomPadding: 25})
    chart.Plot(svg, periodData, "label", key, maxValue)
}

function PlotPeriodPlotChart(key) {
    let svg = document.getElementById(`period-${key}-chart`)

    if (svg === null)
        return

    let chart = new PlotChart({markerColor: key2color[key]})
    chart.Plot(svg, periodData, "label", key)
}

function TogglePeriodChart(key) {
    let block = document.getElementById(`period-${key}-block`)
    block.classList.toggle("analytics-chart-open")
}
