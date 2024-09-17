function GetQuestion() {
    SendRequest("/question", {}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось получить следующий вопрос<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            return
        }

        question.Build(response.question, response.movie, {personId2person: response.person_id2person})
    })
}
