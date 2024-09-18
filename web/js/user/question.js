function SendAnswer(correct, answerTime, buttons) {
    SendRequest("/answer-question", {correct: correct, answer_time: this.answerTime}).then(response => {
        for (let button of buttons)
            button.removeAttribute("disabled")

        if (response.status != SUCCESS_STATUS) {
            ShowNotification(response.message, "error-notification")
            return
        }

        if (response.question === null) {
            ShowNotification(`Не удалось получить следующий вопрос<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            return
        }

        question.Build(response.question, response.movie, {personId2person: response.person_id2person, movieId2scale: response.movie_id2scale})
    })
}

function SendQuizTourAnswer(correct, answerTime, buttons) {
    SendRequest("/answer-quiz-tour-question", {question_id: questionId, correct: correct, answer_time: this.answerTime}).then(response => {
        for (let button of buttons)
            button.removeAttribute("disabled")

        if (response.status != SUCCESS_STATUS) {
            ShowNotification(response.message, "error-notification")
            return
        }

        if (response.redirect) {
            location.href = response.redirect
            return
        }

        questionId = response.question_id
        question.Build(response.question, response.movie, {personId2person: response.person_id2person, movieId2scale: response.movie_id2scale})
    })
}
