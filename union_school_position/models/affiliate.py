from odoo import models, fields, api, _

class Affiliate(models.Model):
    _inherit = 'affiliation.affiliate'

    position_ids = fields.One2many(
        comodel_name='school_position.position',
        inverse_name='affiliate_id',
        string='Positions'
    )
