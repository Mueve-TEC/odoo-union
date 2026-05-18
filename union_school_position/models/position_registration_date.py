# -*- coding: utf-8 -*-

from odoo import models, fields

class PositionRegistrationDate(models.Model):
    _name = 'school_position.registration.date'
    _description = 'Position Registration Date'
    _rec_name = 'date'

    date = fields.Date(string='Registration Date', required=True)
