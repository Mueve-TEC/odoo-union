# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SchoolBenefitType(models.Model):
    _name = 'benefit_request.school_benefit_type'
    _description = 'School benefit\'s type model given by ADIUC'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = [('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
