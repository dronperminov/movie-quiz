function SignIn() {
    let username = GetTextInput("username", "Имя пользователя не заполнено")
    if (username === null)
        return

    let password = GetTextInput("password", "Пароль не заполнен")
    if (password === null)
        return

    let error = document.getElementById("error")
    error.innerText = ""

    let params = new URLSearchParams(window.location.search)
    let redirectUrl = params.get("back_url")

    SendRequest("/sign-in", {username, password}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        localStorage.setItem(TOKEN_NAME, response.token)
        location.href = redirectUrl ? redirectUrl : "/"
    })
}
