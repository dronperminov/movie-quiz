function QuizTour(data, statuses) {
    this.quizTourId = data.quiz_tour_id
    this.quizTourType = data.quiz_tour_type
    this.name = data.name
    this.description = data.description
    this.questionIds = data.question_ids
    this.imageUrl = data.image_url
    this.createdAt = data.created_at
    this.createdBy = data.created_by
    this.tags = data.tags

    this.status = this.quizTourId in statuses ? statuses[this.quizTourId] : null
}

QuizTour.prototype.Build = function() {
    let quizTour = MakeElement("quiz-tour")

    let quizTourImage = MakeElement("quiz-tour-image", quizTour)
    let quizTourImageLink = MakeElement("", quizTourImage, {href: `/quiz-tours/${this.quizTourId}`}, "a")
    MakeElement("", quizTourImageLink, {src: this.imageUrl, loading: "lazy"}, "img")

    if (this.status !== null && this.status.lost == 0) {
        quizTour.classList.add("quiz-tour-completed")
        MakeElement("quiz-tour-completed-text", quizTourImage, {innerText: "Пройден"})
    }

    this.BuildStatus(quizTour)
    this.BuildAnalytics(quizTour, false)

    let quizTourName = MakeElement("quiz-tour-name", quizTour)
    MakeElement("", quizTourName, {href: `/quiz-tours/${this.quizTourId}`, innerText: this.name}, "a")

    MakeElement("quiz-tour-type", quizTour, {innerHTML: `<b>Механика</b>: ${this.QuizTourTypeToRus()}`})
    MakeElement("quiz-tour-description", quizTour, {innerHTML: this.description})
    MakeElement("quiz-tour-tags", quizTour, {innerHTML: `<b>Теги</b>: ${this.tags.map(tag => this.TagToRus(tag)).join(", ")}`})
    this.BuildQuestions(quizTour)

    MakeElement("quiz-tour-date", quizTour, {innerHTML: `${ParseDateTime(this.createdAt).date}`})

    return quizTour
}

QuizTour.prototype.BuildPage = function(blockId) {
    let quizTour = document.getElementById(blockId)

    let quizTourImage = MakeElement("quiz-tour-image", quizTour)
    MakeElement("", quizTourImage, {src: this.imageUrl, loading: "lazy"}, "img")

    MakeElement("quiz-tour-name", quizTour, {innerText: this.name}, "h1")
    MakeElement("quiz-tour-description", quizTour, {innerHTML: this.description})

    this.BuildAnalytics(quizTour, true)

    MakeElement("quiz-tour-type", quizTour, {innerHTML: `<b>Механика</b>: ${this.QuizTourTypeToRus()}`})
    MakeElement("quiz-tour-tags", quizTour, {innerHTML: `<b>Теги</b>: ${this.tags.map(tag => this.TagToRus(tag)).join(", ")}`})
}

QuizTour.prototype.QuizTourTypeToRus = function() {
    let type2rus = {
        "regular": "классический",
        "alphabet": "алфавит",
        "stairs": "лесенка",
        "letter": "на одну букву",
        "n_letters": "N букв",
        "miracles_field": "поле чудес",
        "chain": "цепочка"
    }

    return type2rus[this.quizTourType]
}

QuizTour.prototype.TagToRus = function(tag) {
    let tag2rus = {
        "top": "топовое",
        "soviet": "советское",
        "cartoon": "мультфильмы",
        "series": "сериалы",
        "movie": "фильмы",
        "anime": "аниме",
        "mcs": "КМС"
    }

    return tag2rus[tag]
}

QuizTour.prototype.IsStarted = function() {
    return this.status !== null && this.status.lost < this.questionIds.length
}

QuizTour.prototype.BuildStatus = function(quizTour) {
    if (!this.IsStarted())
        return

    let status = MakeElement("quiz-tour-status", quizTour)

    if (this.status.correct > 0)
        MakeElement("quiz-tour-status-bar quiz-tour-status-bar-correct", status, {style: `width: ${this.status.correct / this.questionIds.length * 100}%`})

    if (this.status.incorrect > 0)
        MakeElement("quiz-tour-status-bar quiz-tour-status-bar-incorrect", status, {style: `width: ${this.status.incorrect / this.questionIds.length * 100}%`})

    if (this.status.lost > 0)
        MakeElement("quiz-tour-status-bar quiz-tour-status-bar-lost", status, {style: `width: ${this.status.lost / this.questionIds.length * 100}%`})

    MakeElement("quiz-tour-time", quizTour, {innerHTML: `<b>время</b>: ${FormatTotalTime(this.status.time.total)}`})
}

QuizTour.prototype.BuildAnalytics = function(quizTour, titleCase) {
    if (this.status === null)
        return

    if (this.status.finished_count > 0) {
        let users = GetWordForm(this.status.finished_count, ["игрок", "игрока", "игроков"])
        let color = `hsl(${this.status.mean_score * 1.2}, 70%, 50%)`
        let circle = `<div class="circle" style="background-color: ${color}"></div>`
        let label = titleCase ? "Cредний балл" : "средний балл"
        MakeElement("quiz-tour-analytics", quizTour, {innerHTML: `<b>${label}:</b> ${circle}${Math.round(this.status.mean_score * 10) / 10}% (${users})`})
    }
}

QuizTour.prototype.BuildQuestions = function(quizTour) {
    let rating = ""

    if (this.IsStarted()) {
        let percent = Math.round(this.status.correct / this.questionIds.length * 1000) / 10
        rating = ` (<span class="correct-color">${GetWordForm(this.status.correct, ['балл', 'балла', 'баллов'])}, ${percent}%</span>)`
    }

    let questions = GetWordForm(this.questionIds.length, ['вопрос', 'вопроса', 'вопросов'])
    MakeElement("quiz-tour-questions", quizTour, {innerHTML: `${questions}${rating}`})
}
