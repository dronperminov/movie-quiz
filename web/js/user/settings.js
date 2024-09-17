function UpdateMainSettings() {
    let settings = {
        show_progress: document.getElementById("show-progress").checked,
        show_knowledge_status: document.getElementById("show-knowledge-status").checked
    }

    SendRequest("/main_settings", settings).then(response => {
        if (response.status != SUCCESS_STATUS)
            ShowNotification(`<b>Ошибка</b>: не удалось обновить настройки<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
        else
            ShowNotification(`Настройки успешно обновлены`, "success-notification", 1000)
    })
}

function UpdateQuestionSettings() {
    let settings = GetQuestionSettings()
    if (settings === null)
        return

    SendRequest("/question_settings", settings).then(response => {
        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`<b>Ошибка</b>: не удалось обновить настройки вопросов<br><b>Причина</b>: ${response.message}`, "error-notification", 3500)
            return
        }

        let movies = GetWordForm(response.movies, ["КМС удовлетворяет", "КМС удовлетворяют", "КМС удовлетворяют"])
        ShowNotification(`Настройки вопросов успешно обновлены<br>${movies} выбранным настройкам`, "success-notification", 1000)
    })
}
