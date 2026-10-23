from odoo import _, fields, models


class Affiliate(models.Model):
    _inherit = "affiliation.affiliate"

    benefit_request_ids = fields.One2many(related="partner_id.benefit_request_ids")

    def _get_unlink_blockers(self):
        blockers = super()._get_unlink_blockers()
        count = (
            self.env["benefit_request.benefit_request"].sudo().search_count([("partner_id", "in", self.partner_id.ids)])
        )
        if count:
            blockers.append(_("%s benefit request(s)") % count)
        return blockers
