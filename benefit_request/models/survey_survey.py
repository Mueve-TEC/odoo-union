# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Survey(models.Model):
    _inherit = 'survey.survey'
    
    generate_benefit = fields.Boolean(string='It create request', default=False)
    request_type_id = fields.Many2one(
        comodel_name='benefit_request.request_type',
        string='Benefit type'
    )
    school_benefit_type_id = fields.Many2one(
        comodel_name='benefit_request.school_benefit_type',
        string='School benefit type'
    )