function BuildTopPlayers(players, topCount = 15) {
    let leaderboard = document.getElementById("leaderboard")

    if (players.length == 0) {
        leaderboard.innerHTML = "Для формирования топа недостаточно квизов, удовлетворяющих заданным параметрам"
        return
    }

    if (players.length >= 3) {
        let top3Players = MakeElement("top3-players", leaderboard)

        for (let i of [1, 0, 2]) {
            let user = players[i][0]

            let topPlayer = MakeElement("top3-player", top3Players)
            MakeElement("top-player-name", topPlayer, {innerText: user.full_name})
            MakeElement("top-player-tours-count", topPlayer, {innerText: GetWordForm(players[i][2], ['мини-квиз', 'мини-квиза', 'мини-квизов'])})

            let image = MakeElement("top-player-image", topPlayer)
            let link = MakeElement("", image, {href: `/analytics?username=${user.username}`}, "a")
            MakeElement("", link, {src: user.avatar_url}, "img")
            MakeElement("top-player-place", image, {innerText: i + 1})

            let flag = MakeElement("top-player-flag", topPlayer)
            let rating = MakeElement("top-player-rating", flag)
            MakeElement("", rating, {src: "/images/rating.svg"}, "img")
            MakeElement("", rating, {innerText: ` ${players[i][1]}`}, "span")
        }
    }

    let topPlayers = MakeElement("top-players", leaderboard)

    for (let i = players.length > 3 ? 3 : 0; i < players.length && i < topCount; i++) {
        let user = players[i][0]

        let topPlayer = MakeElement("top-player", topPlayers)

        MakeElement("top-player-place", topPlayer, {innerText: i + 1})

        let image = MakeElement("top-player-image", topPlayer)
        let link = MakeElement("", image, {href: `/analytics?username=${user.username}`}, "a")
        MakeElement("", link, {src: user.avatar_url}, "img")

        let name = MakeElement("top-player-name", topPlayer, {innerText: user.full_name})
        MakeElement("top-player-tours-count", name, {innerText: GetWordForm(players[i][2], ['мини-квиз', 'мини-квиза', 'мини-квизов'])})

        let rating = MakeElement("top-player-rating", topPlayer)
        MakeElement("", rating, {src: "/images/rating.svg"}, "img")
        MakeElement("", rating, {innerText: ` ${players[i][1]}`}, "span")
    }
}

function ShowTopPlayers() {
    let loader = document.getElementById("loader")
    loader.classList.remove("hidden")

    let tags = tagsInput.GetValue()
    tagsInput.Disable()

    let leaderboard = document.getElementById("leaderboard")
    leaderboard.innerHTML = ""

    SendRequest("/get-top-players", {tags: tags}).then(response => {
        tagsInput.Enable()
        loader.classList.add("hidden")

        if (response.status != SUCCESS_STATUS) {
            ShowNotification(`Не удалось получить данные об игроках<br><b>Причина:</b> ${response.message}`, "error-notification", 3500)
            return
        }

        BuildTopPlayers(response.players)
    })
}
