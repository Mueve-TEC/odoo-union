from odoo import models, fields, api, _

class Affiliate(models.Model):
    _inherit = 'affiliation.affiliate'

    position_ids = fields.One2many(
        comodel_name='school_position.position',
        inverse_name='affiliate_id',
        string='Positions'
    )
    
    position_type_ids = fields.Many2many(
        comodel_name='school_position.type',
        string='Position Types',
        compute='_compute_position_types',
        store=True
    )
    
    @api.depends('position_ids', 'position_ids.type_id')
    def _compute_position_types(self):
        for affiliate in self:
            affiliate.position_type_ids = affiliate.position_ids.mapped('type_id')
