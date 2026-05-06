# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AffiliateContributionCode(models.Model):
    _name = 'contribution.affiliate_contribution_code'
    _description = 'Union affiliates contribution code entity'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    enabled = fields.Boolean(string='Enabled', default=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.code
