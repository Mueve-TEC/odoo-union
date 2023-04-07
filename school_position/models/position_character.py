# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PositionCharacter(models.Model):
    _name = 'school_position.character'
    _description = 'Character of school position'
    _rec_name = 'code'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description", required=True)