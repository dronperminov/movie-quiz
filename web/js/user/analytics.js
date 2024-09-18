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
