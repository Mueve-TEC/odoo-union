# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PositionCharacter(models.Model):
    _name = 'school_position.character'
    _description = 'Character of school position'
    _rec_name = 'code'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description", required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|',('name', operator, name),('code', operator, name)]
        if 'import_file' in self.env.context:
            domain = [('code', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
