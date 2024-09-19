function Question(sendAnswer, mechanics = "regular") {
    this.block = document.getElementById("question")
    this.sendAnswer = sendAnswer
    this.mechanics = mechanics
}

Question.prototype.Build = function(question, movie, params) {
    this.question = question
    this.questionType = this.question.question_type
    this.answer = question.answer

    this.params = params
    this.movie = new Movie(movie, params)
    this.block.innerHTML = ""

    MakeElement("question-title", this.block, {innerHTML: this.question.title})

    this.BuildSpecific()
    this.BuildMechanic()
    this.BuildShowAnswerButton()
    this.BuildAnswerBlock()

    this.answerTime = performance.now()
}

Question.prototype.BuildMechanic = function() {
    if (this.mechanics === "regular")
        return

    let isFirst = this.question.title.startsWith("Вопрос 1 из")

    if (this.mechanics === "alphabet" || (!isFirst && (this.mechanics == "letter" || this.mechanics == "chain"))) {
        let block = MakeElement("question-letter", this.block)
        let letter = this.movie.GetFirstLetter()
        MakeElement("letter", block, {innerText: letter})
        MakeElement("language", block, {innerText: GetLetterLanguage(letter)})
        return
    }

    if (this.mechanics == "miracles_field") {
        let block = MakeElement("miracles-field", this.block)
        let topLetter = this.movie.GetMiraclesFieldLetter()

        for (let letter of this.movie.name.toUpperCase()) {
            let cell = MakeElement(letter == " " ? "space" : "", block)
            MakeElement(letter == topLetter ? "" : "hidden", cell, {innerText: letter}, "span")
        }

        MakeElement("miracles-field-language", this.block, {innerText: GetLetterLanguage(topLetter)})
    }

    if (!isFirst && (this.mechanics === "stairs" || this.mechanics === "n_letters")) {
        let block = MakeElement("question-letter", this.block)
        let length = this.movie.GetNameLength()
        MakeElement("letter", block, {innerText: length})
        MakeElement("language", block, {innerText: GetWordForm(length, ["буква", "буквы", "букв"], true)})
        return
    }
}

Question.prototype.BuildSpecific = function() {
    if (this.questionType == "movie_by_image") {
        let image = MakeElement("question-image", this.block)
        MakeElement("", image, {src: "https://movie-quiz.plush-anvil.ru" + this.question.image_url}, "img")
    }
    else if (this.questionType == "movie_by_slogan") {
        MakeElement("question-text", this.block, {innerText: this.question.slogan})
    }
    else if (this.questionType == "movie_by_short_description" || this.questionType == "movie_by_description") {
        MakeElement("question-text", this.block, {innerHTML: this.movie.GetSpoileredText(this.question.description)})
    }
    else if (this.questionType == "movie_by_actors") {
        let actors = MakeElement("question-actors", this.block)

        for (let actor of this.question.actors) {
            let block = MakeElement("question-actor", actors)
            let person = this.params.personId2person[`${actor.person_id}`]

            if (this.question.hide_actor_photos)
                block.classList.add("question-actor-blur")

            let img = MakeElement("", block, {src: person.photo_url}, "img")
            img.addEventListener("click", () => block.classList.remove("question-actor-blur"))

            MakeElement("link", block, {href: `/persons/${person.person_id}`, innerText: person.name}, "a")
        }
    }
    else if (this.questionType == "movie_by_characters") {
        let characters = this.question.characters.map(character => `<li>${character}</li>`).join("")
        MakeElement("question-text", this.block, {innerHTML: `<ul>${characters}</ul>`})
    }

    for (let spoiler of document.getElementsByClassName("spoiler"))
        spoiler.classList.add("spoiler-hidden")
}

Question.prototype.BuildShowAnswerButton = function() {
    let button = MakeElement("basic-button gradient-button", this.block, {id: "show-answer", innerText: "Показать ответ"}, "button")
    button.addEventListener("click", () => {
        this.answerTime = (performance.now() - this.answerTime) / 1000
        this.ShowAnswer()
    })
}

Question.prototype.BuildAnswerBlock = function() {
    let block = MakeElement("answer-block hidden", this.block, {id: "answer"})
    MakeElement("answer", block, {innerHTML: `<b>Ответ:</b> ${this.answer}`})
    MakeElement("description hidden", block, {innerHTML: `<b>Время ответа:</b> <span id="answer-time"></span>`})

    let buttons = MakeElement("answer-buttons", block)
    let answerCorrectButton = MakeElement("basic-button green-button", buttons, {id: "answer-button-correct", innerText: "Знаю"})
    let answerIncorrectButton = MakeElement("basic-button red-button", buttons, {id: "answer-button-incorrect", innerText: "Не знаю"})

    answerCorrectButton.addEventListener("click", () => this.SendAnswer(true))
    answerIncorrectButton.addEventListener("click", () => this.SendAnswer(false))

    infos.Clear()
    infos.Add(this.movie.BuildInfo())
    block.appendChild(this.movie.Build())
}

Question.prototype.ShowAnswer = function(correct = null) {
    let answerTimeSpan = document.getElementById("answer-time")
    answerTimeSpan.innerText = FormatTime(this.answerTime)
    answerTimeSpan.parentNode.classList.remove("hidden")

    let showAnswerButton = document.getElementById("show-answer")
    showAnswerButton.classList.add("hidden")

    let answerBlock = document.getElementById("answer")
    answerBlock.classList.remove("hidden")

    for (let spoiler of document.getElementsByClassName("spoiler"))
        spoiler.classList.remove("spoiler-hidden")

    for (let miraclesField of document.getElementsByClassName("miracles-field"))
        for (let div of miraclesField.getElementsByTagName("span"))
            div.classList.remove("hidden")

    this.UpdateAnswerButtons(correct)
}

Question.prototype.UpdateAnswerButtons = function(correct = null) {
    if (correct === null)
        return

    let buttons = {
        "true": document.getElementById("answer-button-correct"),
        "false": document.getElementById("answer-button-incorrect")
    }

    for (let [value, button] of Object.entries(buttons)) {
        button.setAttribute("disabled", "")
        if (value !== `${correct}`)
            button.classList.add("hidden")
    }
}

Question.prototype.SendAnswer = function(correct) {
    this.UpdateAnswerButtons(correct)

    let buttons = [document.getElementById("answer-button-correct"), document.getElementById("answer-button-incorrect")]
    this.sendAnswer(correct, this.answerTime, buttons)
}
