# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AffiliateState(models.Model):
    _name = 'affiliation.affiliate_state'
    _description = 'Union affiliate\'s state entity'
    _order = 'order asc'

    name = fields.Char(string='name', required=True)
    enabled = fields.Boolean(string='Enabled', default=True)
    order = fields.Integer(string='order', default=1)