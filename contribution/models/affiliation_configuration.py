# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AffiliationConfiguration(models.Model):
    _inherit = 'affiliation.affiliation_configuration'

    create_user_from_contribution = fields.Boolean(string='Create user on contribution import', default=False)
    