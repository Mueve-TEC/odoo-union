from odoo import fields, models


class AffiliationConfiguration(models.Model):
    _inherit = "affiliation.affiliation_configuration"

    create_user_from_request = fields.Boolean(string="Create affiliate when importing requests", default=False)
