# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BenefitRequest(models.Model):
    _name = 'benefit_request.benefit_request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_type_id = fields.Many2one(
        comodel_name='benefit_request.request_type',
        string='Type',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Applicant',
        required=True
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('requested', 'Requested'),
            ('authorized', 'Authorized'),
            ('rejected', 'Rejected'),
            ('finalized', 'Finalized'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='requested',
    )
    request_date = fields.Date(
        string='Request date', required=True, default=fields.Date.today())
    last_change_state = fields.Date(string='Last change of state')
    last_state = fields.Char(string='Last state')
    full_doc = fields.Boolean(string='Full documentation', default=False)
    expedient = fields.Char(string='Expedient/resolution')
    observations = fields.Text(string='Observations')
    notes = fields.Text(string='Notes')
    responsible = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        required=True,
        default=lambda self: self.env.user
    )
    school_benefit_ids = fields.One2many(
        comodel_name='benefit_request.school_benefit',
        inverse_name='benefit_request_id',
        string='School benefits'
    )
    requested_amount = fields.Float(string='Requested amount')
    authorized_amount = fields.Float(string='Authorized amount')
    accountabled_amount = fields.Float(string='Accountable amount')
    paid_amount = fields.Float(string='Paid amount')

    hide_school_benefits = fields.Boolean(computed='_onchange_request_type')
    hide_amounts = fields.Boolean(computed='_onchange_request_type')
    hide_notes = fields.Boolean(computed='_onchange_request_type')

    @api.onchange('request_type_id')
    def _onchange_request_type(self):
        _groups = self.request_type_id.request_group_ids.mapped('name')
        self.hide_notes = False if 'Notas' in _groups else True
        self.hide_amounts = False if 'Subsidios' in _groups else True
        self.hide_school_benefits = False if 'Bolsones' in _groups else True

        if self.request_type_id.who_apply == 'affiliates':
            return {'domain': {'partner_id': [('type', '=', 'affiliated')]}}
        return {'domain': {'partner_id': False}}

    def authorize(self):
        if self.hide_amounts == False:  # Se deben chequear montos
            if self.authorized_amount <= 0:
                raise ValidationError(
                    _('Authorized amount must be major to zero'))
        if self.hide_school_benefits == False:  # Se deben chequear los bolsones
            if len(self.school_benefit_ids) < 1:
                raise ValidationError(
                    _('There must be at least one school benefit'))
        if not self.request_type_id.meet_reqs(self.partner_id):
            raise ValidationError(
                _('The beneficiary does not meet the requirements'))
        self.state = 'authorized'

    def reject(self):
        self.state = 'rejected'

    def finalize(self):
        if self.hide_amounts == False:  # Se deben chequear montos
            if self.paid_amount <= 0 or self.paid_amount > self.authorized_amount:
                raise ValidationError(
                    _('The paid amount must be major to 0 and minor to authorized amount'))
        if not self.full_doc:
            raise ValidationError(_('The documentation must be completed'))
        self.state = 'finalized'

    def cancel(self):
        self.state = 'canceled'

    def _register_change_state(self, vals):
        vals.update({
            'last_change_state': fields.Date.today(),
            'last_state': self.state
        })

    def write(self, vals):
        if 'state' in vals:
            self._register_change_state(vals)
        if 'partner_id' in vals:
            self.message_unsubscribe([self.partner_id.id])
            self.message_subscribe([vals['partner_id']])
        res = super(BenefitRequest, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals.update({'state': 'requested'})
        res = super(BenefitRequest, self).create(vals)
        if 'partner_id' in vals:
            res.message_subscribe([vals['partner_id']])
        return res

    def name_get(self):
        result = []
        for record in self:
            result.append((record.request_type_id.name, record.partner_id.name))
        return result