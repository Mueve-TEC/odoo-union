# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PositionType(models.Model):
    _name = 'school_position.type'
    _description = 'Type of school position'
    _rec_name = 'code'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description", required=True)
    in_hours = fields.Boolean(string="Is in hours", required=True)
    dedication = fields.Char(string="Dedication", required=True)