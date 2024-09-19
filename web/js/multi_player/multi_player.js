function ErrorSessionId(message) {
    let input = document.getElementById("session-id")
    input.classList.add("error-input")
    input.focus()

    ShowNotification(message, "error-notification", 3500)
}

function InputSessionId() {
    let input = document.getElementById("session-id")
    input.classList.remove("error-input")
}

function GetSessionId() {
    let input = document.getElementById("session-id")
    let sessionId = input.value.trim()
    input.value = sessionId

    if (sessionId === "") {
        ErrorSessionId("Идентификатор сессии не может быть пустым")
        return null
    }

    if (sessionId.match(/^[a-z\d_\-]+$/gi) === null) {
        ErrorSessionId("Идентификатор сессии должен состоять только из латинских символов и цифр")
        return null
    }

    return sessionId
}

function CreateSession() {
    let sessionId = GetSessionId()
    if (sessionId === null)
        return

    SendRequest("/create-multiplayer-session", {session_id: sessionId}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось создать сессию с идентификатором "${sessionId}"<br><b>Причина</b>: ${response.message}`)
            localStorage.removeItem("sessionId")
            return
        }

        multiPlayer.Connect(sessionId, response.username)
    })
}

function ConnectSession() {
    let sessionId = GetSessionId()
    if (sessionId === null)
        return

    let removeStatistics = document.getElementById("remove-statistics-on-connect").checked

    SendRequest("/check-multiplayer-session", {session_id: sessionId, remove_statistics: removeStatistics}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось подключиться к сессии с идентификатором "${sessionId}"<br><b>Причина</b>: ${response.message}`)
            localStorage.removeItem("sessionId")
            return
        }

        let url = new URL(window.location.href)
        url.searchParams.delete("session_id")
        window.history.replaceState(null, "", url.toString())

        multiPlayer.Connect(sessionId, response.username)
    })
}

function UpdateQuestionSettings() {
    let settings = GetQuestionSettings(true)
    if (settings === null)
        return

    multiPlayer.UpdateQuestionSettings(settings)
}

function ShowQuestionSettings(settings) {
    document.getElementById("hide-actor-photos").checked = settings.hide_actor_photos

    answerTimeInput.SetValue(settings.answer_time)
    movieTypesInput.SetValue(settings.movie_types)
    productionInput.SetValue(settings.production)
    votesInput.SetValue(settings.votes)
    yearsInput.SetValue(GetYearsDict(settings.years))
    questionTypesInput.SetValue(settings.question_types)
    repeatIncorrectProbabilityInput.SetValue(Math.round(settings.repeat_incorrect_probability * 100))
}

function Load() {
    let sessionId = localStorage.getItem("sessionId")
    if (sessionId === null)
        return

    let input = document.getElementById("session-id")
    input.value = sessionId
    ConnectSession()
}
