from odoo import api, fields, models


class SchoolBenefitType(models.Model):
    _name = "benefit_request.school_benefit_type"
    _description = "School benefit's type model given by ADIUC"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        domain = list(domain or [])
        search_domain = [("name", operator, name)]
        recs = self.search(search_domain + domain, limit=limit)
        return [(r.id, r.display_name) for r in recs]
