# -*- coding: utf-8 -*-

from odoo import fields, models


class Affiliate(models.Model):
    _inherit = 'affiliation.affiliate'

    benefit_request_ids = fields.One2many(related='partner_id.benefit_request_ids')
