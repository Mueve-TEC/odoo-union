# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AffiliateState(models.Model):
    _name = 'benefit_request.affiliate_state'
    _description = 'State od affiliate'

    name = fields.Char(string='name', required=True)
    value = fields.Char(string='value', required=True)
