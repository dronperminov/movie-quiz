function MultiPlayer() {
    this.ws = null
    this.sessionId = null
    this.username = null

    this.question = null
    this.pageHeaderBlock = document.getElementById("page-header")
    this.questionBlock = document.getElementById("question")
    this.managerBlock = document.getElementById("multi-player-manager")

    this.sessionInfo = document.getElementById("session-info")
    this.usersCountSpan = document.getElementById("connected-users-count")
    this.usersBlock = document.getElementById("connected-users")
    this.sessionIdSpan = document.getElementById("session-id-span")
    this.statisticsBlock = document.getElementById("session-statistics")
    this.statisticsItems = document.getElementById("session-statistics-items")
    this.chatMessagesBlock = document.getElementById("session-chat-messages")
    this.historyBlock = document.getElementById("session-history")
    this.historyActionsBlock = document.getElementById("session-history-actions")
    this.username2avatar = {}

    this.connectionBlock = document.getElementById("connection-block")
    this.removeSessionButton = document.getElementById("remove-session-button")
    this.settingsBlock = document.getElementById("session-settings")
    this.showedSettings = false

    this.chatInput = document.getElementById("session-chat-text")
    this.chatSend = document.getElementById("session-chat-send")
    this.chatInput.addEventListener("input", () => this.InputChatText())
    this.chatInput.addEventListener("keyup", (e) => { if (e.keyCode == 13) this.SendChatMessage()})
    this.chatSend.addEventListener("click", () => this.SendChatMessage())

    this.reactionBlock = document.getElementById("reactions")
}

MultiPlayer.prototype.Connect = function(sessionId, username) {
    this.sessionId = sessionId
    this.username = username

    this.ws = new WebSocket(this.GetWebsockerUrl(sessionId))
    this.ws.onopen = () => this.Open()
    this.ws.onmessage = (e) => this.HandleMessage(e.data)
    this.ws.onclose = () => this.Close()
    this.ws.onerror = (error) => this.HandleError(error)
}

MultiPlayer.prototype.Open = function() {
    this.managerBlock.classList.add("hidden")
    this.historyBlock.classList.remove("hidden")
    this.historyActionsBlock.innerHTML = ""
    this.statisticsBlock.classList.remove("hidden")
    this.reactionBlock.classList.remove("hidden")
    this.connectionBlock.classList.remove("hidden")
    document.querySelector("body").classList.add("hidden-menu")

    localStorage.setItem("sessionId", this.sessionId)

    ShowNotification(`Подключение к сессии ${this.sessionId} установлено<br>Меню будет скрыто на время игры`, "success-notification", 2500)
}

MultiPlayer.prototype.Close = function() {
    this.ws = null

    if (this.sessionId === null) {
        ShowNotification("Подключение к сессии разорвано", "success-notification", 1500)
        return
    }

    ShowNotification(`Подключение к сессии ${this.sessionId} неожиданно разорвано, пробую переподключиться`, "error-notification", 1500)
    setTimeout(() => this.Connect(this.sessionId, this.username), 1000)
}

MultiPlayer.prototype.Disconnect = function() {
    if (this.ws === null)
        return

    this.sessionId = null
    this.username = null
    this.ws.close()

    this.managerBlock.classList.remove("hidden")

    if (this.historyActionsBlock.children.length == 0)
        this.historyBlock.classList.add("hidden")

    this.reactionBlock.classList.add("hidden")
    this.connectionBlock.classList.add("hidden")
    this.sessionInfo.classList.add("hidden")
    document.querySelector("body").classList.remove("hidden-menu")
    this.ClearQuestion()
    this.showedSettings = false

    localStorage.removeItem("sessionId")
}

MultiPlayer.prototype.RemoveSession = function() {
    if (this.sessionId === null)
        return

    if (!confirm("Вы уверены, что хотите удалить сессию?"))
        return

    this.ws.send(JSON.stringify({action: "remove", username: this.username}))
    this.Disconnect()
}

MultiPlayer.prototype.GetWebsockerUrl = function(sessionId) {
    let protocol = location.protocol == "https:" ? "wss" : "ws"
    let host = window.location.host

    return `${protocol}://${host}/ws/${sessionId}`
}

MultiPlayer.prototype.HandleMessage = function(message) {
    if (message === "ping") {
        this.ws.send("pong")
        return
    }

    let session = JSON.parse(message)

    if (session.action == "remove") {
        this.AppendHistory(session)
        this.Disconnect()
        return
    }

    if (session.action == "message" || session.action == "reaction") {
        this.AppendHistory(session)
        return
    }

    this.UpdateSessionInfo(session)

    if (!this.showedSettings || session.action == "settings") {
        ShowQuestionSettings(session.question_settings)
        this.showedSettings = true
    }

    if (session.question === null || session.players.length < 2)
        this.ClearQuestion()
    else if (this.question === null || this.question.movie.movieId != session.question.movie_id || session.action == "question")
        this.InitQuestion(session)
}

MultiPlayer.prototype.HandleError = function(error) {
    ShowNotification(`Произошла ошибка вебсокета: ${JSON.stringify(error)}`, "error-notification", 5000)
    this.Disconnect()
}

MultiPlayer.prototype.UpdateSessionInfo = function(session) {
    if (session.players.length > 0)
        this.sessionInfo.classList.remove("hidden")
    else
        this.sessionInfo.classList.add("hidden")

    this.sessionIdSpan.innerText = this.sessionId

    this.ShowConnectedUsers(session)
    this.ShowStatistics(session)
    this.AppendHistory(session)
}

MultiPlayer.prototype.ShowConnectedUsers = function(session) {
    this.usersCountSpan.innerText = GetWordForm(session.players.length, ["игрок", "игрока", "игроков"])
    this.usersBlock.innerHTML = ""

    if (session.created_by == this.username) {
        this.removeSessionButton.classList.remove("hidden")
        this.settingsBlock.removeAttribute("disabled")
    }
    else {
        this.removeSessionButton.classList.add("hidden")
        this.settingsBlock.setAttribute("disabled", "")
    }

    for (let user of session.players)
        this.BuildConnectedUser(user, session.answers)
}

MultiPlayer.prototype.ShowStatistics = function(session) {
    this.statisticsItems.innerHTML = ""

    for (let [username, answers] of Object.entries(session.statistics))
        this.BuildUserStatistics(username, answers)

    if (this.statisticsItems.children.length > 0)
        this.statisticsBlock.classList.remove("hidden")
    else
        this.statisticsBlock.classList.add("hidden")
}

MultiPlayer.prototype.BuildConnectedUser = function(user, answers) {
    this.username2avatar[user.username] = user.avatar_url

    let block = MakeElement("connected-user", this.usersBlock)
    MakeElement("", block, {src: user.avatar_url}, "img")

    if (!(user.username in answers))
        return

    if (answers[user.username].correct)
        block.classList.add("answered-correct-user")
    else
        block.classList.add("answered-incorrect-user")
}

MultiPlayer.prototype.BuildUserStatistics = function(username, answers) {
    if (answers.length == 0 || !(username in this.username2avatar))
        return

    let correct = 0
    let incorrect = 0
    let time = 0

    for (let answer of answers) {
        if (answer.correct)
            correct += 1
        else
            incorrect += 1

        time += answer.answer_time
    }

    let meanTime = FormatTime(time / answers.length)
    let correctText = `<span class="correct-color">${GetWordForm(correct, ['верный', 'верных', 'верных'])}</span>`
    let incorrectText = `<span class="incorrect-color">${GetWordForm(incorrect, ['неверный', 'неверных', 'неверных'])}</span>`

    let block = MakeElement("session-statistics-item", this.statisticsItems)
    MakeElement("", block, {src: this.username2avatar[username]}, "img")
    MakeElement("", block, {innerHTML: `@${username}: ${correctText}, ${incorrectText} (${meanTime})`})
}

MultiPlayer.prototype.InitQuestion = function(session) {
    let params = {
        personId2person: session.person_id2person,
        movieId2scale: session.movie_id2scale[this.username]
    }

    this.ClearQuestion()

    this.pageHeaderBlock.classList.add("hidden")
    this.question = new Question((correct, answerTime, buttons) => this.AnswerQuestion(correct, answerTime))
    this.question.Build(session.question, session.movie, params)

    if (this.username in session.answers) {
        this.question.answerTime = session.answers[this.username].answer_time
        this.question.ShowAnswer(session.answers[this.username].correct)
    }

    window.scrollTo({top: 0, behavior: 'smooth'})
    this.historyActionsBlock.scrollTop = 0
}

MultiPlayer.prototype.ClearQuestion = function() {
    this.pageHeaderBlock.classList.remove("hidden")
    this.questionBlock.innerHTML = ""
    this.question = null

    infos.Clear()
}

MultiPlayer.prototype.AnswerQuestion = function(correct, answerTime) {
    this.ws.send(JSON.stringify({action: "answer", correct: correct, answer_time: answerTime}))
}

MultiPlayer.prototype.AppendHistory = function(session) {
    if (["connect", "disconnect", "remove", "answer", "settings", "message", "reaction"].indexOf(session.action) == -1)
        return

    let date = new Date()
    let hours = `${date.getHours()}`.padStart(2, '0')
    let minutes = `${date.getMinutes()}`.padStart(2, '0')
    let seconds = `${date.getSeconds()}`.padStart(2, '0')

    let text = null

    if (session.action == "connect") {
        text = `@${session.username} подключился`

        if (session.username != this.username)
            ShowNotification(text, "info-notification", 1500)
    }
    else if (session.action == "disconnect") {
        text = `@${session.username} отключился`

        if (session.username != this.username)
            ShowNotification(text, "info-notification", 1500)
    }
    else if (session.action == "remove" && session.username == session.created_by) {
        text = `@${session.username} удалил сессию`
        ShowNotification(`@${session.username} удалил сессию`, "error-notification", 4000)
    }
    else if (session.action == "answer") {
        let correct = session.answers[session.username].correct ? '<span class="correct">знаю</span>' : '<span class="incorrect">не знаю</span>'
        let time = FormatTime(session.answers[session.username].answer_time)
        text = `@${session.username} ответил ${correct} (${time})`

        ShowNotification(session.username == this.username ? `Вы ответили ${correct} (${time})` : text, "info-notification", 1500)
    }
    else if (session.action == "settings") {
        let author = session.username == this.username ? "Вы обновили" : `@${session.username} обновил`
        text = `@${session.username} обновил настройки вопросов`
        ShowNotification(`${author} настройки вопросов`, "info-notification", 1800)
    }
    else if (session.action == "message") {
        let author = session.username == this.username ? "Вы" : `@${session.username}`
        text = `@${session.username}: ${session.text}`
        ShowNotification(`${author}: ${session.text}`, "info-notification", 1800)
    }
    else if (session.action == "reaction") {
        text = `@${session.username} отправил <img class="reaction" src="/images/reactions/${session.reaction}.svg">`
        ShowNotification(text, "info-notification", 1800)
    }

    let action = MakeElement("session-history-action", null)
    let user = MakeElement("session-history-action-user", action)
    MakeElement("", user, {src: this.username2avatar[session.username]}, "img")
    MakeElement("", action, {innerHTML: `${hours}:${minutes}:${seconds}: ${text}`})

    if (session.action == "message")
        this.chatMessagesBlock.prepend(action.cloneNode(true))

    this.historyActionsBlock.prepend(action)
}

MultiPlayer.prototype.InputChatText = function() {
    if (this.chatInput.value.trim() !== "")
        this.chatSend.classList.remove("session-chat-hidden")
    else
        this.chatSend.classList.add("session-chat-hidden")
}

MultiPlayer.prototype.SendChatMessage = function() {
    let text = this.chatInput.value.trim()
    this.chatInput.value = ""
    this.chatInput.blur()
    this.InputChatText()
    this.ws.send(JSON.stringify({action: "message", text: text}))
}

MultiPlayer.prototype.SendReaction = function(reaction) {
    this.ws.send(JSON.stringify({action: "reaction", reaction: reaction}))
}

MultiPlayer.prototype.UpdateQuestionSettings = function(settings) {
    this.ws.send(JSON.stringify({action: "settings", settings: settings}))
}
