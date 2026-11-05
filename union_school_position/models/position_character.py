from odoo import api, fields, models


class PositionCharacter(models.Model):
    _name = "school_position.character"
    _description = "Character of school position"
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description", required=True)

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        domain = list(domain or [])
        search_domain = ["|", ("name", operator, name), ("code", operator, name)]
        if "import_file" in self.env.context:
            search_domain = [("code", operator, name)]
        recs = self.search(search_domain + domain, limit=limit)
        return [(r.id, r.display_name) for r in recs]
