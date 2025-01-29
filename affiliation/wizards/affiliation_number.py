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
        _to_write = {'affiliation_number': self.affiliation_number }
        
        fields = ['state', 'quote', 'affiliation_date', 'disaffiliation_date']
        for field in fields:
            if self.env.context.get(field):
                _to_write.update({field:self.env.context.get(field)})

        if self.affiliate_id.disaffiliation_date:
            _to_write.update({'disaffiliation_date': None})

        # increment next affiliation number sequence
        self.env['ir.sequence'].next_by_code('next_affiliation_number_seq')

        self.affiliate_id.write(_to_write)

