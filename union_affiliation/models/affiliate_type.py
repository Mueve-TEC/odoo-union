from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AffiliateType(models.Model):
    _name = "affiliation.affiliate_type"
    _description = "Union affiliate's type entity"
    _order = "name asc"

    name = fields.Char(string="Name", required=True)
    enabled = fields.Boolean(string="Enabled", default=True)

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            domain = [("name", "=", rec.name)]
            if rec.id:
                domain.append(("id", "!=", rec.id))
            if self.env["affiliation.affiliate_type"].search(domain, limit=1):
                raise ValidationError(_("There is already exist a type with the same name!"))
