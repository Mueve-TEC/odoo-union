# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PositionType(models.Model):
    _name = 'school_position.type'
    _description = 'Type of school position'
    _rec_name = 'name'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True)
    in_hours = fields.Boolean(string='Is in hours', required=True)
    dedication = fields.Char(string='Dedication', required=True)

    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}' if record.code else record.name
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('code', operator, name)]
        if 'import_file' in self.env.context:
            domain = [('code', operator, name)]
        return self._search(domain + args, limit=limit)
