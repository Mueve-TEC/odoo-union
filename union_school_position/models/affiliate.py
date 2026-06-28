from odoo import api, fields, models


class Affiliate(models.Model):
    _inherit = 'affiliation.affiliate'

    position_ids = fields.One2many(
        comodel_name='school_position.position',
        inverse_name='affiliate_id',
        string='Positions',
    )

    position_registration_date_ids = fields.Many2many(
        comodel_name='school_position.registration.date',
        string='Fechas de registro de cargos',
        compute='_compute_position_registration_dates',
        store=True,
        readonly=True,
    )

    has_featured_position = fields.Boolean(
        string='Has featured position',
        default=False,
        compute='_compute_has_featured_position',
        store=True,
        readonly=True,
    )

    @api.depends('position_ids', 'position_ids.featured')
    def _compute_has_featured_position(self):
        for affiliate in self:
            affiliate.has_featured_position = any(affiliate.position_ids.mapped('featured'))

    @api.depends('position_ids', 'position_ids.registration_date')
    def _compute_position_registration_dates(self):
        date_model = self.env['school_position.registration.date'].sudo()
        for affiliate in self:
            dates = affiliate.position_ids.mapped('registration_date')
            dates = set([d for d in dates if d])

            if not dates:
                affiliate.position_registration_date_ids = False
                continue

            date_records = date_model.browse()
            for d in dates:
                existing = date_model.search([('date', '=', d)], limit=1)
                if not existing:
                    existing = date_model.create({'date': d})
                date_records |= existing

            affiliate.position_registration_date_ids = date_records
