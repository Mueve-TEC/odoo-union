# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AffiliationNumber(models.TransientModel):
    _name = 'affiliation.affiliation_number'
    _description = 'Model for Affiliation Number wizard'

    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate',
        string='Affiliate',
        required=True
    )
    affiliation_number = fields.Integer(string='Affiliation number', required=True)

    def confirm(self):
        _to_write = {'affiliation_number': self.affiliation_number, 'state': 'affiliated'}
        if 'affiliation_date' in self.env.context:
            _to_write.update({'affiliation_date': self.env.context['affiliation_date']})
        self.affiliate_id.write(_to_write)

