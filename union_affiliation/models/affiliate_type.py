# -*- coding: utf-8 -*-

from odoo import fields, models


class AffiliateType(models.Model):
    _name = "affiliation.affiliate_type"
    _description = "Union affiliate's type entity"
    _order = "name asc"

    name = fields.Char(string="Name", required=True)
    enabled = fields.Boolean(string="Enabled", default=True)

    _sql_constraints = [
        (
            "unique_name",
            "unique(name)",
            "There is already exist a type with the same name!",
        ),
    ]
