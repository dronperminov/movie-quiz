function Production(value) {
    this.value = value
    this.options = {
        "russian": "российское",
        "korean": "корейское",
        "turkish": "турецкое",
        "foreign": "зарубежное"
    }
}

Production.prototype.ToRus = function() {
    return this.options[this.value]
}

function ProductionList(productions) {
    this.productions = productions.map(production => new Production(production))
}

ProductionList.prototype.ToRus = function() {
    return this.productions.map(production => production.ToRus()).join(", ")
}
