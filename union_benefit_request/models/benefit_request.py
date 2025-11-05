# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BenefitRequest(models.Model):
    _name = 'benefit_request.benefit_request'
    _description = 'Benefit request for partners'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_type_id = fields.Many2one(
        comodel_name='benefit_request.request_type',
        string='Type',
        required=True,
        ondelete='restrict'
    )
    
    # This is not related to the affiliate table because there are requests that can be made by people who are not affiliates.
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Applicant',
        required=True,
        ondelete='restrict'
    )
    # The next two fields only will be used to filters
    affiliate_uid = fields.Char(string='Affiliate UID', compute='_compute_uid', store=True)
    affiliate_personal_id = fields.Char(string='Personal ID', compute='_compute_personal_id', store=True)
    
    # Field for import process - maps to affiliate by UID
    import_uid = fields.Char(string='Legajo')
    
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
    paid_amount = fields.Float(string='Paid amount')

    hide_school_benefits = fields.Boolean(computed='_onchange_request_type')
    hide_amounts = fields.Boolean(computed='_onchange_request_type')
    hide_notes = fields.Boolean(computed='_onchange_request_type')
    
    survey_user_input_id = fields.Many2one(
        comodel_name='survey.user_input'
    )

    email = fields.Char(related='partner_id.email', store=False)

    @api.onchange('request_type_id')
    def _onchange_request_type(self):
        _groups = self.request_type_id.request_group_ids.mapped('name')
        self.hide_notes = False if 'Notas' in _groups else True
        self.hide_amounts = False if 'Subsidios' in _groups else True
        self.hide_school_benefits = False if 'Bolsones' in _groups else True

        if self.request_type_id.who_apply == 'affiliates':
            sql='SELECT partner_id FROM affiliation_affiliate'
            self.env.cr.execute(sql)
            ids = list(map(lambda x: x['partner_id'], self.env.cr.dictfetchall()))
            return {'domain': {'partner_id': [('id', 'in', ids)]}}
        return {'domain': {'partner_id': False}}

    @api.depends('request_type_id')
    def _compute_hides(self):
        _groups = self.request_type_id.request_group_ids.mapped('name')
        self.hide_notes = False if 'Notas' in _groups else True
        self.hide_amounts = False if 'Subsidios' in _groups else True
        self.hide_school_benefits = False if 'Bolsones' in _groups else True

    def authorize(self):
        self._compute_hides()
        if self.hide_amounts == False:  
            if self.authorized_amount <= 0:
                raise ValidationError(
                    _('Authorized amount must be major to zero'))
        if self.hide_school_benefits == False: 
            if len(self.school_benefit_ids) < 1:
                raise ValidationError(
                    _('There must be at least one school benefit'))
        if self.request_type_id.meet_reqs(self.partner_id):
            self.state = 'authorized'

    def reject(self):
        self.state = 'rejected'

    def finalize(self):
        self._compute_hides()
        if self.hide_amounts == False:
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
            'last_state': _(self.state)
        })

    def write(self, vals):
        if 'state' in vals:
            self._register_change_state(vals)
        if 'partner_id' in vals:
            self.message_unsubscribe([self.partner_id.id])
            self.message_subscribe([vals['partner_id']])

        _groups = self.request_type_id.request_group_ids.mapped('name')
        if len(_groups):
            vals['hide_notes'] = False if 'Notas' in _groups else True
            vals['hide_amounts'] = False if 'Subsidios' in _groups else True
            vals['hide_school_benefits'] = False if 'Bolsones' in _groups else True


        res = super(BenefitRequest, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        # Am I importing data?
        if 'import_file' in self.env.context:
            if 'import_uid' in vals:
                affiliate = self.env['affiliation.affiliate'].search([('uid','=',vals['import_uid'])])
                if len(affiliate.ids):
                    vals['partner_id'] = affiliate[0].partner_id.id
                    vals.pop('import_uid')  # Remove after use
                else:
                    raise ValidationError(_('There is not an affiliate with that uid %s' % (vals['import_uid'])))
        
        if 'state' not in vals:
            vals.update({'state': 'requested'})
        res = super(BenefitRequest, self).create(vals)
        if 'partner_id' in vals:
            res.message_subscribe([vals['partner_id']])
        res._compute_hides()
        return res

    def name_get(self):
        result = []
        for record in self:
            name = '%s, %s, %s' % (record.request_date.strftime("%Y-%m-%d"),record.request_type_id.name, record.partner_id.name)        
            result.append((record.id, _("%s")%(name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = [('request_type_id', operator, name)]
        if 'import_file' in self.env.context:
            _date, _type, _name = name.split(',')
            domain = [('request_date', '=', _date), ('request_type_id', operator, _type)]
            partner = self.env['res.partner'].search([('name', operator, _name)], limit=limit)
            if partner:
                domain = domain + [('partner_id', '=', partner[0].id)]
        else:
            partner = self.env['res.partner'].search([('name', operator, name)], limit=limit)
            if partner:
                domain = ['|', domain[0], ('partner_id', '=', partner[0].id)]

        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    @api.depends('partner_id')
    def _compute_uid(self):
        for record in self:
            if record.partner_id.id:
                affiliate = record.env['affiliation.affiliate'].search([('partner_id','=',record.partner_id.id)])
                if len(affiliate.ids):
                    record.affiliate_uid = affiliate[0].uid

    @api.depends('partner_id')
    def _compute_personal_id(self):
        for record in self:
            if record.partner_id.id:
                affiliate = record.env['affiliation.affiliate'].search([('partner_id','=',record.partner_id.id)])
                if len(affiliate.ids):
                    record.affiliate_personal_id = affiliate[0].personal_id

    def _message_get_suggested_recipients(self):
        recipients = super(BenefitRequest, self)._message_get_suggested_recipients()
        recipients[self.id].append((self.partner_id.id, self.partner_id.name, 'Solicitante'))
        return recipients
