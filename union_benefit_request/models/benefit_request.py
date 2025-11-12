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
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('authorized', 'Authorized'),
            ('rejected', 'Rejected'),
            ('finalized', 'Finalized'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='draft',
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

    def _register_change_state(self, vals):
        vals.update({
            'last_change_state': fields.Date.today(),
            'last_state': _(self.state)
        })
        
        # Log state change in chatter
        state_labels = {
            'draft': _('Draft'),
            'requested': _('Requested'),
            'authorized': _('Authorized'),
            'rejected': _('Rejected'),
            'finalized': _('Finalized'),
            'canceled': _('Canceled')
        }
        
        old_state = state_labels.get(self.state, self.state)
        new_state = state_labels.get(vals['state'], vals['state'])
        
        message = _('State changed from <b>%s</b> to <b>%s</b>') % (old_state, new_state)
        self.message_post(body=message, message_type='notification')
    
    def _get_field_display_value(self, field_name, value):
        """Helper method to get display value for different field types"""
        if value is None or value == False:
            return _('Not set')
        
        field = self._fields.get(field_name)
        
        # Many2one fields
        if field.type == 'many2one':
            if isinstance(value, int):
                record = self.env[field.comodel_name].browse(value)
                return record.name if record else _('Not set')
            return value.name if hasattr(value, 'name') else str(value)
        
        # Boolean fields
        elif field.type == 'boolean':
            return _('Yes') if value else _('No')
        
        # Date fields
        elif field.type == 'date':
            if isinstance(value, str):
                return value
            return value.strftime('%Y-%m-%d') if value else _('Not set')
        
        # Float fields
        elif field.type == 'float':
            return str(value)
        
        # Text and Char fields
        else:
            return str(value) if value else _('Not set')
    
    def _log_school_benefits_changes(self, commands):
        """Log changes in school benefits (One2many)"""
        for command in commands:
            # Command format: (0, 0, {values}) = create, (1, id, {values}) = update, (2, id) = delete
            if command[0] == 0:  # Create
                message = _('<b>School Benefit</b> added')
                self.message_post(body=message, message_type='notification')
            elif command[0] == 1:  # Update
                benefit_id = command[1]
                benefit = self.env['benefit_request.school_benefit'].browse(benefit_id)
                if benefit.exists():
                    message = _('<b>School Benefit</b> "%s" updated') % benefit.name_get()[0][1]
                    self.message_post(body=message, message_type='notification')
            elif command[0] == 2:  # Delete
                benefit_id = command[1]
                benefit = self.env['benefit_request.school_benefit'].browse(benefit_id)
                if benefit.exists():
                    message = _('<b>School Benefit</b> "%s" removed') % benefit.name_get()[0][1]
                    self.message_post(body=message, message_type='notification')
            elif command[0] == 3:  # Unlink (remove relation but don't delete)
                benefit_id = command[1]
                benefit = self.env['benefit_request.school_benefit'].browse(benefit_id)
                if benefit.exists():
                    message = _('<b>School Benefit</b> "%s" unlinked') % benefit.name_get()[0][1]
                    self.message_post(body=message, message_type='notification')
            elif command[0] == 5:  # Unlink all
                message = _('<b>All School Benefits</b> removed')
                self.message_post(body=message, message_type='notification')
            elif command[0] == 6:  # Replace with list
                message = _('<b>School Benefits</b> list replaced')
                self.message_post(body=message, message_type='notification')

    def write(self, vals):
        # Track field changes for logging
        tracked_fields = {
            'request_type_id': _('Type'),
            'partner_id': _('Applicant'),
            'request_date': _('Request date'),
            'full_doc': _('Full documentation'),
            'expedient': _('Expedient/resolution'),
            'observations': _('Observations'),
            'notes': _('Notes'),
            'responsible': _('Responsible'),
            'requested_amount': _('Requested amount'),
            'authorized_amount': _('Authorized amount'),
            'paid_amount': _('Paid amount'),
        }
        
        # Log changes for tracked fields
        for field_name, field_label in tracked_fields.items():
            if field_name in vals:
                old_value = self._get_field_display_value(field_name, getattr(self, field_name))
                new_value = self._get_field_display_value(field_name, vals[field_name])
                
                if old_value != new_value:
                    message = _('<b>%s</b> changed from "%s" to "%s"') % (
                        field_label, old_value, new_value
                    )
                    self.message_post(body=message, message_type='notification')
        
        # Track changes in school benefits (One2many)
        if 'school_benefit_ids' in vals:
            self._log_school_benefits_changes(vals['school_benefit_ids'])
        
        if 'state' in vals:
            self._register_change_state(vals)
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
            vals.update({'state': 'draft'})
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
