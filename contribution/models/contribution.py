# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AffiliateContribution(models.Model):
    _name = 'contribution.affiliate_contribution'
    _description = 'Union affiliates contribution entity'

    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate',
        string='Affiliate',
        required=True
    )
    date = fields.Date(string='Date', required=True)
    contrib_amount = fields.Float('Amount', required=True)
    contribution_code_id = fields.Many2one(
        comodel_name='contribution.affiliate_contribution_code',
        string='Code',
        required=True
    )

    @api.model
    def create(self, vals):
        # Am I importing data?
        if 'import_file' in self.env.context:
            affiliate = self.env['affiliation.affiliate'].search([('uid','=',vals['legajo'])])
            if len(affiliate.ids):
                affiliate = affiliate[0]
                vals['affiliate_id'] = affiliate.id
            # else:


        res = super(AffiliateContribution, self).create(vals)
        return res

