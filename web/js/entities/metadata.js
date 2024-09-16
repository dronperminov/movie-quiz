function Metadata(metadata, createText, updateText) {
    this.createdAt = metadata.created_at
    this.createdBy = metadata.created_by
    this.updatedAt = metadata.updated_at
    this.updatedBy = metadata.updated_by
    this.createText = createText
    this.updateText = updateText
}

Metadata.prototype.BuildInfo = function(parent, className = "info-line") {
    let created = ParseDateTime(this.createdAt)
    MakeElement(className, parent, {innerHTML: `<b>${this.createText}:</b> ${created.date} в ${created.time} пользователем @${this.createdBy}`})

    if (this.createdAt == this.updatedAt)
        return

    let updated = ParseDateTime(this.updatedAt)
    MakeElement(className, parent, {innerHTML: `<b>${this.updateText}:</b> ${updated.date} в ${updated.time} пользователем @${this.updatedBy}`})
}
