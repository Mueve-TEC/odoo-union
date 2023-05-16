# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Query(models.Model):
    _name = 'inconsistencies.query'
    _description = 'Query of inconsistency of Affiliate\'s state'

    from_date = fields.Date(string='From', required=True)
    to_date = fields.Date(string='To', required=True)
    query_date = fields.Date(string='Query date', readonly=True, required=True, default=fields.Date.today())
    description = fields.Char(string='Description', required=True)
    contribute = fields.Boolean(
        string='Contribute', 
        help="Include people who contributed and should not have contributed",
        required=True
    )
    not_contribute = fields.Boolean(
        string='Doesn\'t contribute',
        help="Include people who didn't contribute and should have contributed",
        required=True
    )
    affiliate_type_id = fields.Many2one(
        comodel_name='affiliation.affiliate_type',
        string='Type'
    )

    @api.depends('from_date', 'to_date')
    def query_inconsistencies(self):
        if self.from_date >= self.to_date :
            raise ValidationError(_('To date should be major to from date'))

        result = False

        if self.affiliate_type_id:
            if self.not_contribute :
                self.env.cr.execute("select calcInconsByType(%s, %s, %s, %s, %s)", ('no_aporto', self.from_date, self.to_date, self.description, self.affiliate_type_id.id))
                result = True if len(self.env.cr.fetchall()) >= 1 else result
                # self.env['docentes.gestion_de_cambios'].invalidate_cache()

            if self.contribute:
                self.env.cr.execute("select calcInconsByType(%s, %s, %s, %s, %s)", ('aporto', self.from_date, self.to_date, self.description, self.affiliate_type_id.id))
                result = True if len(self.env.cr.fetchall()) >= 1 else result
                # self.env['docentes.gestion_de_cambios'].invalidate_cache()

            self.env.cr.execute("select calcInconsStateByType(%s, %s, %s, %s)", (self.from_date, self.to_date, self.description, self.affiliate_type_id.id))
            result = True if len(self.env.cr.fetchall()) >= 1 else result
        else:
            if self.not_contribute :
                self.env.cr.execute("select calculateInconsistencies(%s, %s, %s, %s)", ('no_aporto', self.from_date, self.to_date, self.description))
                result = True if len(self.env.cr.fetchall()) >= 1 else result
                # self.env['docentes.gestion_de_cambios'].invalidate_cache()

            if self.contribute:
                self.env.cr.execute("select calculateInconsistencies(%s, %s, %s, %s)", ('aporto', self.from_date, self.to_date, self.description))
                result = True if len(self.env.cr.fetchall()) >= 1 else result
                # self.env['docentes.gestion_de_cambios'].invalidate_cache()
            
            self.env.cr.execute("select calculateInconsistentStates(%s, %s, %s)", (self.from_date, self.to_date, self.description))
            result = True if len(self.env.cr.fetchall()) >= 1 else result

        if not result :
            raise ValidationError(_('There aren\'t inconsistencies between that dates'))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Gestión de cambios',
            'res_model': 'inconsistencies.result',
            # 'res_id': id_ge.id,
            # 'taget': 'new',
            'views': [[False, 'tree']],
            'domain': [['description', "=", self.description]]
            # 'view_mode': 'tree',
            # 'view_type': 'tree'
        }
