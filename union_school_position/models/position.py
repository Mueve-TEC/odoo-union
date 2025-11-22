# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Position(models.Model):
    _name = 'school_position.position'
    _description = 'School position'

    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate',
        string='Affiliate',
        ondelete='restrict'
    )
    type_id = fields.Many2one(
        comodel_name='school_position.type',
        string='Type',
        ondelete='restrict'
    )
    position_number = fields.Char(string="Position number")
    hs_amount = fields.Integer(string="Hours amount")
    character_id = fields.Many2one(
        comodel_name='school_position.character',
        string='Character',
        ondelete='restrict'
    )
    workplace_id = fields.Many2one(
        comodel_name='union.workplace',
        string='Workplace',
        ondelete='restrict',
        help='Workplace where the position is held'
    )
    date_from = fields.Date(
        string='From',
        help='Position start date'
    )
    date_to = fields.Date(
        string='To',
        help='Position end date (if applicable)'
    )
    registration_date = fields.Date(
        string='Registration date',
        help='Position information date.'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes or observations about the position'
    )
    # The next fields are to manage the importation process
    # It needs to be stored because it is necessary for the import process
    import_uid = fields.Char(string='Import UID')
    import_personal_id = fields.Char(string='Import Personal ID')

    # Related fields for filters
    uid = fields.Char(related='affiliate_id.uid', store=False)
    personal_id = fields.Char(related='affiliate_id.personal_id', store=False)
    dedication = fields.Char(
        related='type_id.dedication', 
        string='Dedication', 
        store=False, 
        readonly=True,
        help='Dedication of the position type'
    )
    type_description = fields.Char(
        related='type_id.name', 
        string='Type description', 
        store=False, 
        readonly=True,
        help='Description of the position type'
    )
    type_code = fields.Char(
        related='type_id.code', 
        string='Type code', 
        store=False, 
        readonly=True,
        help='Code of the position type'
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_to <= record.date_from:
                    raise ValidationError(_('The end date must be later than the start date.'))

    @api.constrains('registration_date')
    def _check_registration_date(self):
        for record in self:
            if record.registration_date:
                if record.registration_date > fields.Date.today():
                    raise ValidationError(_('The registration date cannot be in the future.'))

    def name_get(self):
        result = []
        for record in self:
            name = '%s,%s' % (record.type_id.name, record.affiliate_id.name)        
            result.append((record.id, _("%s")%(name)))
        return result

    @api.model
    def create(self, vals):
        # Am I importing data?
        if 'import_file' in self.env.context:
            affiliate = None
            if 'import_uid' in vals:
                affiliate = self.env['affiliation.affiliate'].search(
                    [('uid', '=', vals['import_uid'])])
            else:
                if 'import_personal_id' in vals:
                    affiliate = self.env['affiliation.affiliate'].search(
                        [('personal_id', '=', vals['import_personal_id'])])
            if len(affiliate.ids):
                vals['affiliate_id'] = affiliate[0].id
            else:
                raise ValidationError(_('Affiliate doesn\'t exist!.'))
            self._clean_affiliate_data(vals)
        res = super(Position, self).create(vals)
        return res

    def write(self,vals):

        res = super(Position, self).write(vals)
        return res

    def _clean_affiliate_data(self, vals):
        vals.pop('import_uid') if 'import_uid' in vals else None
        vals.pop('import_personal_id') if 'personal_id' in vals else None
            
