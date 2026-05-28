# -*- coding: utf-8 -*-

from odoo import models, fields

class AffiliationConfiguration(models.Model):
    _inherit = 'affiliation.affiliation_configuration'

    create_user_from_request = fields.Boolean(
        string='Create affiliate when importing requests',
        default=False
    )
