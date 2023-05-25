# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PositionDependency(models.Model):
    _name = 'school_position.dependency'
    _description = 'Dependency of school position'
    _rec_name = 'code'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    parent_id= fields.Many2one(
        comodel_name='school_position.dependency', 
        string='Parent',
        ondelete='restrict'
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|',('name', operator, name),('code', operator, name)]
        if 'import_file' in self.env.context:
            domain = [('code', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
