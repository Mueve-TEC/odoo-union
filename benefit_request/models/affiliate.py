# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Affiliate(models.Model):
    _inherit = 'affiliation.affiliate'
    
    benefit_request_ids = fields.One2many(related='partner_id.benefit_request_ids')