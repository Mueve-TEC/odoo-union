from odoo import api, fields, models


class PositionType(models.Model):
    _name = "school_position.type"
    _description = "Type of school position"
    _rec_name = "name"
    _rec_names_search = ["code", "name"]

    _code_unique = models.Constraint(
        "unique(code)",
        "There is already a position type with the same code!",
    )
    _name_unique = models.Constraint(
        "unique(name)",
        "There is already a position type with the same description!",
    )

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description", required=True)
    in_hours = fields.Boolean(string="Is in hours", required=True)
    dedication = fields.Char(string="Dedication", required=True)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.code}] {record.name}" if record.code else record.name
