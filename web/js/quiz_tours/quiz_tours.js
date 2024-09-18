function GetSearchParams() {
    return {
        query: document.getElementById("query").value.trim(),
        completed_type: document.getElementById("completed-type").value,
        quiz_tour_types: quizTourTypeInput.GetValue(),
        tags: tagsInput.GetValue()
    }
}

function LoadQuizTours(response, block) {
    for (let quizTour of response.quiz_tours) {
        quizTour = new QuizTour(quizTour, response.statuses)
        block.appendChild(quizTour.Build())
    }

    return response.quiz_tours.length
}

function PushUrlParams(params = null) {
    let url = new URL(window.location.href)

    ClearSearchParams(url)

    if (params !== null) {
        if (params.query !== "")
            url.searchParams.set("query", params.query)

        url.searchParams.set("completed_type", params.completed_type)

        for (let key of ["quiz_tour_types", "tags"])
            if (Object.keys(params[key]).length > 0)
                url.searchParams.set(key, JSON.stringify(params[key]))
    }

    window.history.pushState(null, '', url.toString())
}

function SearchQuizTours() {
    let params = GetSearchParams()
    if (params === null)
        return

    PushUrlParams(params)

    search.CloseFiltersPopup()
    infiniteScroll.Reset()
    infiniteScroll.LoadContent()
}

function ClearQuizTours() {
    infiniteScroll.Reset()
    PushUrlParams()
}
