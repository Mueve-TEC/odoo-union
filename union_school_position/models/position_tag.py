# -*- coding: utf-8 -*-

from odoo import fields, models


class PositionTag(models.Model):
    _name = "school_position.tag"
    _description = "Tag of school position"

    name = fields.Char(string="Name", required=True)
