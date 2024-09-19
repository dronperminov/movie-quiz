function GetYearsList(yearsSettings) {
    let years = []

    for (let [year, value] of Object.entries(yearsSettings)) {
        let [startYear, endYear] = year.split("-")
        if (startYear !== "")
            startYear = +startYear

        if (endYear !== "")
            endYear = +endYear

        years.push({start_year: startYear, end_year: endYear, value: value})
    }

    return years
}

function GetYearsDict(yearsSettings) {
    let years = {}

    for (let year of yearsSettings)
        years[`${year.start_year}-${year.end_year}`] = year.value

    return years
}

function GetQuestionSettings(yearsToList = false) {
    let answerTime = answerTimeInput.GetValue()
    if (answerTime === null)
        return null

    let hideActorPhotos = document.getElementById("hide-actor-photos").checked

    let movieTypes = movieTypesInput.GetValue()
    if (movieTypes === null)
        return null

    let production = productionInput.GetValue()
    if (production === null)
        return null

    let years = yearsInput.GetValue()
    if (years === null)
        return null

    let votes = votesInput.GetValue()
    if (votes === null)
        return null

    let questionTypes = questionTypesInput.GetValue()
    if (questionTypes === null)
        return null

    let repeatIncorrectProbability = repeatIncorrectProbabilityInput.GetValue()
    if (repeatIncorrectProbability === null)
        return null

    return {
        answer_time: answerTime,
        movie_types: movieTypes,
        production: production,
        years: yearsToList ? GetYearsList(years) : years,
        votes: votes,
        question_types: questionTypes,
        hide_actor_photos: hideActorPhotos,
        repeat_incorrect_probability: repeatIncorrectProbability / 100,
    }
}
