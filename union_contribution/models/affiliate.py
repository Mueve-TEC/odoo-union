from odoo import _, fields, models


class Affiliate(models.Model):
    _inherit = "affiliation.affiliate"

    contribution_ids = fields.One2many(comodel_name="contribution.affiliate_contribution", inverse_name="affiliate_id")

    def _get_unlink_blockers(self):
        blockers = super()._get_unlink_blockers()
        count = self.env["contribution.affiliate_contribution"].sudo().search_count([("affiliate_id", "in", self.ids)])
        if count:
            blockers.append(_("%s contribution(s)") % count)
        return blockers
