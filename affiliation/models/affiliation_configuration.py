# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AffiliationConfiguration(models.Model):
    _name = 'affiliation.affiliation_configuration'
    _description = 'Configuration of Affiliaton module'

    current_affiliation_number = fields.Integer(string='Current affiliation number')
    next_affiliation_number = fields.Integer(string='Next affiliation number')
    set_affiliation_date = fields.Selection(
        selection=[
            ('on_affiliate','On affiliate'),
            ('on_confirm','On confirm affiliation'),
        ],
        string='Set init of affiliation',
        default='on_confirm'
    )
    set_disaffiliation_date = fields.Selection(
        selection=[
            ('on_disaffiliate','On disaffiliate'),
            ('on_confirm','On confirm disaffiliation'),
        ],
        string='Set end of affiliation',
        default='on_confirm'
    )

    def write(self, vals):
        if 'next_affiliation_number' in vals:
            _seq = self.env['ir.sequence'].search([('code','=','adiuc_affiliation_number_seq')])
            _seq.number_next_actual = vals['next_affiliation_number'] 
        res = super(AffiliationConfiguration, self).write(vals)
        return res