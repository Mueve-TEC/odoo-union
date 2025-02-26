# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Import(models.TransientModel):
    _inherit = 'base_import.import'
    _description = 'Base Import'

    def do(self, fields, columns, options, dryrun=False):
        # Clean logs
        
        res = super(Import, self).do(fields, columns, options, dryrun)
        return res