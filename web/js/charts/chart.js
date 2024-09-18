function Chart(config = null) {
    if (config === null)
        config = {}

    this.radius = config.radius || 25
    this.size = config.size || 25
    this.gap = config.gap || 2
    this.initAngle = config.initAngle || -90
    this.dividerColor = config.dividerColor || "#e1e1e1"
}

Chart.prototype.GetAngles = function(values) {
    let sum = 0

    for (let value of values)
        sum += value

    let angles = []
    for (let i = 0; i < values.length; i++)
        angles.push((i > 0 ? angles[i - 1] : 0) + values[i] / sum * 2 * Math.PI)

    return angles
}

Chart.prototype.MakeSegment = function(svg, startAngle, endAngle, color) {
    let circle = document.createElementNS('http://www.w3.org/2000/svg', "circle")
    let radius = this.radius + this.size / 2

    circle.setAttribute("cx", 0)
    circle.setAttribute("cy", 0)
    circle.setAttribute("r", radius)

    circle.setAttribute("stroke", color)
    circle.setAttribute("stroke-width", this.size)
    circle.setAttribute("fill", "none")
    circle.setAttribute("stroke-dasharray", `${radius * (endAngle - startAngle)}, ${radius * 2 * Math.PI}`)
    circle.setAttribute("transform", `rotate(${(startAngle) / Math.PI * 180 + this.initAngle})`)
    svg.appendChild(circle)
}

Chart.prototype.MakeDivider = function(svg, startAngle, endAngle) {
    if (endAngle >= Math.PI * 2)
        endAngle = 0

    if (startAngle == endAngle)
        return

    let path = document.createElementNS('http://www.w3.org/2000/svg', "path")
    let angle = endAngle + this.initAngle / 180 * Math.PI

    let x1 = this.radius * Math.cos(angle)
    let y1 = this.radius * Math.sin(angle)

    let x2 = (this.radius + this.size) * Math.cos(angle)
    let y2 = (this.radius + this.size) * Math.sin(angle)

    path.setAttribute("stroke", this.dividerColor)
    path.setAttribute("stroke-width", this.gap)
    path.setAttribute("d", `M${x1} ${y1} L${x2} ${y2}`)
    svg.appendChild(path)
}

Chart.prototype.Plot = function(svg, values) {
    svg.setAttribute("viewBox", "-50 -50 100 100 ")
    svg.innerHTML = ''

    let angles = this.GetAngles(values.map(value => value.value))

    for (let i = 0; i < angles.length; i++)
        this.MakeSegment(svg, i > 0 ? angles[i - 1] : 0, angles[i], values[i].color)

    for (let i = 0; i < angles.length; i++)
        if (values[i].value > 0)
            this.MakeDivider(svg, i > 0 ? angles[i - 1] : 0, angles[i])
}
