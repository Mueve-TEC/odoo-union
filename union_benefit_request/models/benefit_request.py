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
        ondelete='restrict',
        tracking=True
    )
    
    # This is not related to the affiliate table because there are requests that can be made by people who are not affiliates.
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Applicant',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    # The next two fields only will be used to filters
    affiliate_uid = fields.Char(string='Affiliate UID', compute='_compute_uid', store=True)
    affiliate_personal_id = fields.Char(string='Personal ID', compute='_compute_personal_id', store=True)
    
    # Field for import process - maps to affiliate by UID
    import_uid = fields.Char(string='Legajo')
    
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('authorized', 'Authorized'),
            ('rejected', 'Rejected'),
            ('finalized', 'Finalized'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='draft',
        tracking=True
    )
    request_date = fields.Date(
        string='Request date', required=True, default=fields.Date.today(), tracking=True)
    last_change_state = fields.Date(string='Last change of state')
    last_state = fields.Char(string='Last state')
    full_doc = fields.Boolean(string='Full documentation', default=False, tracking=True)
    expedient = fields.Char(string='Expedient/resolution', tracking=True)
    observations = fields.Text(string='Observations', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    responsible = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    school_benefit_ids = fields.One2many(
        comodel_name='benefit_request.school_benefit',
        inverse_name='benefit_request_id',
        string='School benefits',
        tracking=True
    )
    requested_amount = fields.Float(string='Requested amount', tracking=True)
    authorized_amount = fields.Float(string='Authorized amount', tracking=True)
    paid_amount = fields.Float(string='Paid amount', tracking=True)

    hide_school_benefits = fields.Boolean(compute='_onchange_request_type')
    hide_amounts = fields.Boolean(compute='_onchange_request_type')
    hide_notes = fields.Boolean(compute='_onchange_request_type')
    
    survey_user_input_id = fields.Many2one(
        comodel_name='survey.user_input'
    )

    email = fields.Char(related='partner_id.email', store=False)

    @api.onchange('request_type_id')
    def _onchange_request_type(self):
        _groups = self.request_type_id.request_group_ids.mapped('name')
        self.hide_notes = False if 'Notas' in _groups else True
        self.hide_amounts = False if 'Importes' in _groups else True
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
        self.hide_amounts = False if 'Importes' in _groups else True
        self.hide_school_benefits = False if 'Bolsones' in _groups else True

    def request(self):
        self._compute_hides()
        if self.hide_amounts == False:  
            if self.requested_amount <= 0:
                raise ValidationError(
                    _('Requested amount must be major to zero')) #traducir
        if self.hide_school_benefits == False: 
            if len(self.school_benefit_ids) < 1:
                raise ValidationError(
                    _('There must be at least one school benefit')) #traducir
        
        self.state = 'requested'

        self.request_date = fields.Date.today()

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
        if self.request_type_id.require_full_doc and not self.full_doc:
            raise ValidationError(_('The documentation must be completed'))
        self.state = 'finalized'

    def cancel(self):
        self.state = 'canceled'

    def set_to_draft(self):
        # Check if user has admin permissions for finalized or canceled states
        if self.state in ['finalized', 'canceled']:
            if not self.env.user.has_group('union_benefit_request.group_benefit_request_admin'):
                raise ValidationError(
                    _('Only users with admin permissions can return finalized or canceled requests to draft state'))
        self.state = 'draft'

    def write(self, vals):
        if 'state' in vals:
            vals.update({
                'last_change_state': fields.Date.today(),
                'last_state': _(self.state)
            })
        if 'partner_id' in vals:
            self.message_unsubscribe([self.partner_id.id])
            self.message_subscribe([vals['partner_id']])

        _groups = self.request_type_id.request_group_ids.mapped('name')
        if len(_groups):
            vals['hide_notes'] = False if 'Notas' in _groups else True
            vals['hide_amounts'] = False if 'Importes' in _groups else True
            vals['hide_school_benefits'] = False if 'Bolsones' in _groups else True

        res = super(BenefitRequest, self).write(vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
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
                vals.update({'state': 'draft'})
        
        res = super(BenefitRequest, self).create(vals_list)
        for record in res:
            vals = vals_list[res.ids.index(record.id)] if res.ids else {}
            if 'partner_id' in vals or record.partner_id:
                partner_id = vals.get('partner_id') or record.partner_id.id
                record.message_subscribe([partner_id])
        res._compute_hides()
        return res

    def _compute_display_name(self):
        for record in self:
            name = '%s - %s' % (record.request_type_id.name, record.partner_id.name)        
            record.display_name = _("%s")%(name)

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
        return [(r.id, r.display_name) for r in recs]

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
        self.ensure_one()
        recipients = super()._message_get_suggested_recipients()

        if not self.partner_id:
            return recipients

        already_present = any(
            r.get('partner_id') == self.partner_id.id
            for r in recipients
        )

        if not already_present:
            recipients.append({
                'partner_id': self.partner_id.id,
                'name': self.partner_id.name,
                'email': self.partner_id.email_normalized,
                'create_values': {},
            })

        return recipients
