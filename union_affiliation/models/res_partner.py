# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    email2 = fields.Char(string='Other email')
    affiliate_id = fields.One2many(
        comodel_name='affiliation.affiliate',
        inverse_name='partner_id',
        string='Affiliate'
    )
    is_affiliate = fields.Boolean(
        string='Is Affiliate',
        compute='_compute_is_affiliate'
    )

    @api.depends('affiliate_id')
    def _compute_is_affiliate(self):
        """Compute if the partner is an affiliate"""
        for partner in self:
            partner.is_affiliate = bool(partner.affiliate_id)

    def action_view_affiliate(self):
        """Open the form view of the associated affiliate"""
        self.ensure_one()
        if not self.affiliate_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': _('Affiliate'),
            'res_model': 'affiliation.affiliate',
            'res_id': self.affiliate_id[0].id,
            'view_mode': 'form',
            'target': 'current',
        }