# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AffiliateContributionCode(models.Model):
    _name = 'contribution.affiliate_contribution_code'
    _description = 'Union affiliates contribution code entity'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    enabled = fields.Boolean(string='Enabled', default=True)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.code))
        return result
