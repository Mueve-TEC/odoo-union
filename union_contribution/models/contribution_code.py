# -*- coding: utf-8 -*-

from odoo import models, fields


class AffiliateContributionCode(models.Model):
    _name = 'contribution.affiliate_contribution_code'
    _description = 'Union affiliates contribution code entity'
    _rec_name = 'description'

    code = fields.Char(string='Code', required=True)
    description = fields.Char(string='Description', required=True)
    enabled = fields.Boolean(string='Enabled', default=True)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.description))
        return result
