# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Position(models.Model):
    _name = 'school_position.position'
    _description = 'School position'

    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate', 
        string='Affiliate'
    )
    type_id = fields.Many2one(
        comodel_name='school_position.type', 
        string='Type'
    )
    position_number = fields.Char(string="Position number")
    hs_amount = fields.Integer(string="Hours amount")
    character_id = fields.Many2one(
        comodel_name='school_position.character', 
        string='Character'
    )
    dependency_id = fields.Many2one(
        comodel_name='school_position.dependency', 
        string='Dependency'
    )
    tag_ids = fields.Many2many(
        comodel_name='school_position.tag', 
        relation='school_position_tag_affiliate_rel', 
        column1='position_id', 
        column2='tag_id',
        string='Tags'
    )

    def name_get(self):
        result = []
        for record in self:
            result.append((record.position_type_id, record.affiliate_id))
        return result