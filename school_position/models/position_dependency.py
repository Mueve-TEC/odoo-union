# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PositionDependency(models.Model):
    _name = 'school_position.dependency'
    _description = 'Dependency of school position'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    parent_id= fields.Many2one(
        comodel_name='school_position.dependency', 
        string='Parent'
    )