from odoo import fields, models


class AffiliateContributionCode(models.Model):
    _name = "contribution.affiliate_contribution_code"
    _description = "Union affiliates contribution code entity"
    _rec_name = "description"

    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)
    enabled = fields.Boolean(string="Enabled", default=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.description
