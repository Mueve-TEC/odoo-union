from odoo import fields, models


class Affiliate(models.Model):
    _inherit = "affiliation.affiliate"

    benefit_request_ids = fields.One2many(related="partner_id.benefit_request_ids")

    def unlink(self):
        requests = (
            self.env["benefit_request.benefit_request"].sudo().search([("partner_id", "in", self.partner_id.ids)])
        )
        requests.unlink()
        return super().unlink()
