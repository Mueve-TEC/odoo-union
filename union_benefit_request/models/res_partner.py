# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    benefit_request_ids = fields.One2many(
        comodel_name='benefit_request.benefit_request',
        inverse_name='partner_id',
    )