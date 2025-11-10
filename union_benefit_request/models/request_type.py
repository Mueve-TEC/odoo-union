# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from .affiliate_state import es_AR_state_names

class RequestType(models.Model):
    _name = 'benefit_request.request_type'
    _description = 'Type of benefits'
    _rec_name = 'name'

    name = fields.Char(string='name', required=True)
    active = fields.Boolean(string="Active", default=True)
    state_ids = fields.Many2many(
        comodel_name='benefit_request.affiliate_state',
        string='States',
        relation='request_type_affiliate_state_rel',
        column1='request_type_id',
        column2='affiliate_state_id'
    )
    quote = fields.Boolean(string='Contributors', default=False)
    who_apply = fields.Selection(
        selection=[('everybody', 'Everybody'),
                   ('affiliates', 'Only affiliates')],
        string='Who can request?',
        default='affiliates'
    )
    request_group_ids = fields.Many2many(
        comodel_name='benefit_request.request_group',
        string='Groups',
        column1='request_type_id',
        column2='request_group_id'
    )
    require_full_doc = fields.Boolean(
        string='Require full documentation',
        default=True,
        help='If checked, full documentation will be required to finalize requests of this type'
    )

    def meet_reqs(self, affiliate):
        if self.who_apply == 'everybody':
            return True
        affiliate = self.env['affiliation.affiliate'].search(
            [('partner_id', '=', affiliate.id)])
        if len(affiliate.ids) == 0:
            return True
        else:
            affiliate = affiliate[0]
        if self._check_state(affiliate) and self._check_quote(affiliate):
            return True

    def _check_state(self, affiliate):
        _state_values = self.state_ids.mapped('value')
        if not len(_state_values):
            return True
        if affiliate.state not in _state_values:
            raise ValidationError(
                _("The beneficiary affiliation state is not valid for this request type.\n\nState: %s.\nValid states: %s.") % (es_AR_state_names[affiliate.state], ', '.join([es_AR_state_names[state] for state in _state_values])))
        return True

    def _check_quote(self, affiliate):
        if affiliate.quote != self.quote:
            raise ValidationError(
                _("The beneficiary quote state is not valid for this request type.\n\nValid quote: %s.") % (self.quote))
        return True
