# -*- coding: utf-8 -*-

from odoo import models, fields, api


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
        selection=[('everybody','Everybody'),('affiliates','Only affiliates')],
        string='Who can request?',
        default='affiliates'
    )
    request_group_ids = fields.Many2many(
        comodel_name='benefit_request.request_group',
        string='Groups',
        column1='request_type_id',
        column2='request_group_id'
    )

    def meet_reqs(self, affiliate):
        if self.who_apply == 'everybody':
            return True
        affiliate = self.env['affiliation.affiliate'].search([('partner_id','=',affiliate.id)])
        if len(affiliate.ids) == 0:
            return True
        else:
            affiliate = affiliate[0]
        return True if (self._check_state(affiliate) and self._check_quote(affiliate)) else False

    def _check_state(self, affiliate):
        _state_names = self.state_ids.mapped('name')
        if not len(_state_names):
            return True
        return True if affiliate.state in _state_names else False

    def _check_quote(self, affiliate):
        return True if affiliate.quote == self.quote else False