# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AffiliationConfiguration(models.Model):
    _name = 'inconsistencies.result'
    _description = 'Result of inconsistencies query about Affiliate\'s state'

    from_date = fields.Date(string='From', readonly=True)
    to_date = fields.Date(string='To', readonly=True)
    query_date = fields.Date(string='Query date', readonly=True)
    description = fields.Char(string='Description', readonly=True)
    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate',
        string='Affiliate',
        required=True,
        ondelete='cascade'
    )
    status = fields.Char(string='Situación', readonly=True)