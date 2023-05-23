# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ButterLog(models.Model):
    _name = 'butterlog.butterlog'
    _description = 'Log model for Odoo events and actions'

    model_name = fields.Char(string='Model')
    model_id = fields.Integer(string='Model ID')
    date = fields.Datetime(string='Date', required=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User'
    )
    type = fields.Selection(
        selection=[
            ('error','Error'),
            ('update','Update'),
            ('delete','Delete'),
            ('info','Info'),
            ('action','Action'),
            ('import','Import')],
        default='info'
    )
    message = fields.Char(string='Message', required=True)