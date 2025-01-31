# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RequestGroup(models.Model):
    _name = 'benefit_request.request_group'
    _description = 'Groups for benefit\'s type'

    name = fields.Char(string='name', required=True)
