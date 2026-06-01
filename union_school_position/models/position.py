# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

log = logging.getLogger(__name__)


class Position(models.Model):
    _name = 'school_position.position'
    _description = 'School position'

    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate',
        string='Affiliate',
        ondelete='restrict',
        required=True
    )
    type_id = fields.Many2one(
        comodel_name='school_position.type',
        string='Type',
        ondelete='restrict',
        required=True
    )
    position_number = fields.Char(string="Position number")
    hs_amount = fields.Integer(string="Hours amount")
    character_id = fields.Many2one(
        comodel_name='school_position.character',
        string='Character',
        ondelete='restrict',
        required=True
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
    import_name = fields.Char(string='Import Name')
    import_vat = fields.Char(string='Import VAT')

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
    type_id_in_hours = fields.Boolean(
        related='type_id.in_hours',
        string='In hours',
        readonly=True
    )
    featured = fields.Boolean(
        string='Featured'
    )
    affiliate_state = fields.Selection(
        related='affiliate_id.state',
        string='Affiliate State',
        store=True
    )

    workplace_level1 = fields.Char(
        string='Workplace Level 1',
        compute='_compute_workplace_levels',
        store=True
    )

    workplace_level2 = fields.Char(
        string='Workplace Level 2',
        compute='_compute_workplace_levels',
        store=True
    )

    workplace_level3 = fields.Char(
        string='Workplace Level 3',
        compute='_compute_workplace_levels',
        store=True
    )

    @api.depends('workplace_id', 'workplace_id.level', 'workplace_id.parent_path')
    def _compute_workplace_levels(self):
        """Computa las agrupaciones jerárquicas por lugar de trabajo"""
        for position in self:
            if not position.workplace_id:
                position.workplace_level1 = 'Sin lugar de trabajo'
                position.workplace_level2 = 'Sin lugar de trabajo'
                position.workplace_level3 = 'Sin lugar de trabajo'
                continue

            workplace = position.workplace_id

            parent_ids = []
            if workplace.parent_path:
                parent_ids = [int(x)
                              for x in workplace.parent_path.split('/') if x]
            else:
                parent_ids = [workplace.id]

            # Ordenar los lugares padres por nivel
            parent_workplaces = self.env['union.workplace'].browse(
                parent_ids).sorted('level')

            level1_workplace = parent_workplaces.filtered(
                lambda w: w.level == 1)
            position.workplace_level1 = level1_workplace[
                0].name if level1_workplace else workplace.name

            level2_workplace = parent_workplaces.filtered(
                lambda w: w.level == 2)
            position.workplace_level2 = (
                level2_workplace[0].name if level2_workplace
                else position.workplace_level1
            )

            position.workplace_level3 = workplace.name

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
    @api.constrains('hs_amount')
    def _check_hs_amount(self):
        for record in self:
            if record.type_id.in_hours and (record.hs_amount is None or record.hs_amount <= 0):
                raise ValidationError(_('The hours amount must be greater than zero for positions in hours.'))
            if not record.type_id.in_hours and record.hs_amount:
                raise ValidationError(_('The hours amount must be empty for positions that are not in hours.'))
    def name_get(self):
        result = []
        for record in self:
            name = '%s,%s' % (record.type_id.name, record.affiliate_id.name)        
            result.append((record.id, _("%s")%(name)))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        # Am I importing data?
        if 'import_file' in self.env.context:
            for vals in vals_list:
                if not vals.get('affiliate_id'):
                    affiliate = False
                    if vals.get('import_uid'):
                        affiliate = self.env['affiliation.affiliate'].search([('uid', '=', vals['import_uid'])], limit=1)

                    if affiliate:
                        vals['affiliate_id'] = affiliate.id
                        
                    else:
                        conf = self.env['affiliation.affiliation_configuration'].browse(1)
                        if conf.create_user_from_position:
                            new_uid = vals.get('import_uid')
                            import_name = vals.get('import_name')
                            
                            if not new_uid or not import_name:
                                error_msg = _("Cannot create affiliate for position import. Missing import_name or ID (import_uid). "
                                              "Please ensure the imported data includes both Name and ID.")
                                raise ValidationError(error_msg)
                                
                            if not str(new_uid).isdigit():
                                raise ValidationError(_("El campo ID debe contener únicamente números."))
                            if str(new_uid)[0] == '0':
                                raise ValidationError(_("El campo ID no puede comenzar con cero."))
                                
                            new_affiliate_vals = {
                                'state': 'new',
                                'uid': new_uid,
                                'name': import_name
                            }
                            
                            if vals.get('import_personal_id'):
                                new_affiliate_vals['personal_id'] = vals.get('import_personal_id')
                            if vals.get('import_vat'):
                                new_affiliate_vals['vat'] = vals.get('import_vat')
                                 
                            new_affiliate = self.env['affiliation.affiliate'].create(new_affiliate_vals)
                            vals['affiliate_id'] = new_affiliate.id
                        else:
                            error_msg = _(
                                "Affiliate does not exist in the database (UID: %s, Personal ID: %s), "
                                "and the option to auto-create them during import is disabled in the configuration."
                            ) % (vals.get('import_uid', 'N/A'), vals.get('import_personal_id', 'N/A'))
                            raise ValidationError(error_msg)
                self._clean_affiliate_data(vals)
        res = super(Position, self).create(vals_list)
        return res

    def write(self,vals):

        res = super(Position, self).write(vals)
        return res

    def _clean_affiliate_data(self, vals):
        vals.pop('import_uid', None)
        vals.pop('import_personal_id', None)
        vals.pop('import_name', None)
        vals.pop('import_vat', None)
            
    def action_set_featured(self):
        for record in self:
            record.featured = True
            
    def action_unset_featured(self):
        for record in self:
            record.featured = False

    def on_import_error(self, line, error):
        _message = {
            'line': int(error['record']) + 1,
            'record': str(line),
            'error': error['message']
        }
        self.env.user.notify_danger(message=(_('There were errors during importation. See the logs!')))