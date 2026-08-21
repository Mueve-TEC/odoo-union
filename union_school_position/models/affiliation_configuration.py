# -*- coding: utf-8 -*-

from odoo import fields, models


class AffiliationConfiguration(models.Model):
    _inherit = "affiliation.affiliation_configuration"

    create_user_from_position = fields.Boolean(
        string="Create affiliate when importing positions", default=False
    )
