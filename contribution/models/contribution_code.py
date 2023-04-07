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

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain = ['|', ('name', operator, name), ('name', operator, name)]
    #     partners = self.env['res.partner'].search([('name', operator, name)], limit=limit)
    #     if partners:
    #         domain = ['|'] + domain + [('partner_id', 'in', partners.ids)]
    #     recs = self.search(domain + args, limit=limit)
    #     return recs.name_get()