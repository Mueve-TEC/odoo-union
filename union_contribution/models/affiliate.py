# -*- coding: utf-8 -*-

from odoo import fields, models


class Affiliate(models.Model):
    _inherit = 'affiliation.affiliate'

    contribution_ids = fields.One2many(comodel_name='contribution.affiliate_contribution', inverse_name='affiliate_id')
