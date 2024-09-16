const SWIPE_HANDLER_DOWN = "down"
const SWIPE_HANDLER_UP = "up"
const SWIPE_HANDLER_LEFT = "left"
const SWIPE_HANDLER_RIGHT = "right"
const SWIPE_HANDLER_VERTICAL = "vertical"
const SWIPE_HANDLER_HORIZONTAL = "horizontal"

function SwipeHandler(block, onSwipe, direction, swipePart = 150, moveDelta = 10) {
    this.block = block
    this.onSwipe = onSwipe

    this.direction = direction
    this.swipePart = swipePart
    this.moveDelta = moveDelta
    this.isPressed = false

    this.block.addEventListener("transitionend", (e) => this.block.style.transform = "")

    this.block.addEventListener("mousedown", (e) => this.MouseDown(this.GetPoint(e)))
    this.block.addEventListener("mousemove", (e) => this.MouseMove(this.GetPoint(e)))
    this.block.addEventListener("mouseup", (e) => this.MouseUp())
    this.block.addEventListener("mouseleave", (e) => this.MouseUp())

    this.block.addEventListener("touchstart", (e) => this.MouseDown(this.GetPoint(e)))
    this.block.addEventListener("touchmove", (e) => this.MouseMove(this.GetPoint(e)))
    this.block.addEventListener("touchend", (e) => this.MouseUp())
    this.block.addEventListener("touchleave", (e) => this.MouseUp())
}

SwipeHandler.prototype.GetPoint = function(e) {
    if (this.block.scrollTop > 10)
        return null

    if (e.touches)
        return {x: e.touches[0].clientX, y: e.touches[0].clientY, e: e}

    return {x: e.clientX, y: e.clientY, e: e}
}

SwipeHandler.prototype.MouseDown = function(point) {
    if (point === null)
        return

    this.isPressed = true
    this.prevX = point.x
    this.prevY = point.y
    this.deltaX = 0
    this.deltaY = 0
}

SwipeHandler.prototype.GetDeltaX = function(x) {
    if ([SWIPE_HANDLER_UP, SWIPE_HANDLER_DOWN, SWIPE_HANDLER_VERTICAL].indexOf(this.direction) > -1)
        return 0

    let dx = x - this.prevX

    if (this.direction == SWIPE_HANDLER_LEFT && dx > 0)
        return 0

    if (this.direction == SWIPE_HANDLER_RIGHT && dx < 0)
        return 0

    return dx
}

SwipeHandler.prototype.GetDeltaY = function(y) {
    if ([SWIPE_HANDLER_LEFT, SWIPE_HANDLER_RIGHT, SWIPE_HANDLER_HORIZONTAL].indexOf(this.direction) > -1)
        return 0

    let dy = y - this.prevY

    if (this.direction == SWIPE_HANDLER_UP && dy > 0)
        return 0

    if (this.direction == SWIPE_HANDLER_DOWN && dy < 0)
        return 0

    return dy
}

SwipeHandler.prototype.IsSwiped = function() {
    return Math.abs(this.deltaX) >= this.moveDelta || Math.abs(this.deltaY) >= this.moveDelta
}

SwipeHandler.prototype.MouseMove = function(point) {
    if (!this.isPressed || point === null)
        return

    this.deltaX = this.GetDeltaX(point.x)
    this.deltaY = this.GetDeltaY(point.y)

    if (!this.IsSwiped())
        return

    point.e.preventDefault()
    this.block.style.transform = `translate(${this.deltaX}px, ${this.deltaY}px)`
}

SwipeHandler.prototype.CheckDelta = function(delta, size) {
    if (this.swipePart < 1)
        return Math.abs(delta) > size * this.swipePart

    return Math.abs(delta) > this.swipePart
}

SwipeHandler.prototype.MouseUp  = function() {
    this.isPressed = false

    if (this.IsSwiped()) {
        if (this.CheckDelta(this.deltaX, this.block.clientWidth) || this.CheckDelta(this.deltaY, this.block.clientHeight))
            this.onSwipe()
        else
            this.block.style.transform = `translate(0, 0)`
    }

    this.deltaX = 0
    this.deltaY = 0
}
