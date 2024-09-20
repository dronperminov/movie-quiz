function PlayerCollection(config = null) {
    this.players = []
    this.config = config === null ? {withIcons: true} : config
}

PlayerCollection.prototype.Add = function(trackId, audio) {
    let player = new Player(trackId, audio, this.config)
    this.players.push(player)
    return player
}

PlayerCollection.prototype.Pause = function(audio) {
    for (let player of this.players)
        if (player.audio !== audio)
            player.Pause()
}

PlayerCollection.prototype.GetPlayer = function() {
    if (this.players.length == 0)
        return null

    return this.players[this.players.length - 1]
}

PlayerCollection.prototype.Clear = function() {
    for (let player of this.players)
        player.Pause()

    this.players = []
}

PlayerCollection.prototype.Reset = function() {
    for (let player of this.players)
        player.Reset()
}