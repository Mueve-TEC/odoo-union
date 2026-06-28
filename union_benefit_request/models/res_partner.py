# -*- coding: utf-8 -*-

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    benefit_request_ids = fields.One2many(
        comodel_name='benefit_request.benefit_request',
        inverse_name='partner_id',
    )
