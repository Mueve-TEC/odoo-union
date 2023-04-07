# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RequestGroup(models.Model):
    _name = 'benefit_request.request_group'

    name = fields.Char(string='name', required=True)
