# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Import(models.TransientModel):
    _inherit = 'base_import.import'
    _description = 'Base Import'

    def do(self, fields, columns, options, dryrun=False):
        # Clean logs
        old_logs = self.env['butterlog.butterlog'].search([('user_id','=',self.env.user.id),('model_name','=',self.res_model),('type','=','import')])
        old_logs.unlink()
        res = super(Import, self).do(fields, columns, options, dryrun)
        return res