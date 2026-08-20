# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class AffiliateContribution(models.Model):
    _name = 'contribution.affiliate_contribution'
    _description = 'Union affiliates contribution entity'

    affiliate_id = fields.Many2one(
        comodel_name='affiliation.affiliate',
        string='Affiliate',
        required=True,
        ondelete='restrict'
    )
    date = fields.Date(string='Date', required=True)
    contrib_amount = fields.Float('Amount', required=True)
    contribution_code_id = fields.Many2one(
        comodel_name='contribution.affiliate_contribution_code',
        string='Code',
        required=True,
        ondelete='restrict'
    )
    # The next fields are to manage the importation process
    # All need be stored, because are necessary for the import process 
    import_name = fields.Char(string='Import name')
    import_uid = fields.Char(string='Import uid')
    import_vat = fields.Char(string='Import vat')
    import_personal_id = fields.Char(string='Import personal ID')

    uid = fields.Char(related='affiliate_id.uid', store=False)
    personal_id = fields.Char(related='affiliate_id.personal_id', store=False)

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('import_file'):
            vals_list = [self._prepare_import_vals(vals) for vals in vals_list]
        res = super(AffiliateContribution, self).create(vals_list)
        return res

    def write(self, vals):
        res = super(AffiliateContribution, self).write(vals)
        return res

    def on_import_error(self, line, error):
        _message = {
            'line': int(error['record']) + 1,
            'record': str(line),
            'error': error['message']
        }
        log = {
            'user_id': self.env.user.id,
            'date': str(fields.Datetime.now()),
            'model_name': self._name,
            'model_id': -1,
            'type': 'import',
            'message': str(_message)
        }
        self.env.user.notify_danger(message=(_('There were errors during importation. See the logs!')))


    def _compute_display_name(self):
        for record in self:
            name = '%s,%s' % (record.affiliate_id.name, record.date.strftime("%Y-%m-%d"))        
            record.display_name = _("%s")%(name)

    def _clean_data_affiliate(self, vals):
        vals.pop('import_name') if 'import_name' in vals else None
        vals.pop('import_uid') if 'import_uid' in vals else None
        vals.pop('import_vat') if 'import_vat' in vals else None
        vals.pop('import_personal_id') if 'import_personal_id' in vals else None

    def _prepare_import_vals(self, vals):
        """Resolve or create affiliate during contribution import.

        Expected import keys are: import_uid, import_name, import_vat, import_personal_id.
        """
        import_uid = vals.get('import_uid')
        if not str(import_uid).isdigit():
            raise ValidationError(_("El campo ID debe contener únicamente números."))
        if str(import_uid)[0] == '0':
            raise ValidationError(_("El campo ID no puede comenzar con cero."))

        import_name = vals.get('import_name')
        import_vat = vals.get('import_vat')
        import_personal_id = vals.get('import_personal_id')

        # If affiliate is already resolved by import mapping, just clear helper fields.
        if vals.get('affiliate_id'):
            self._clean_data_affiliate(vals)
            return vals

        affiliate_model = self.env['affiliation.affiliate']
        affiliate = affiliate_model.browse()

        if import_uid:
            affiliate = affiliate_model.search([('uid', '=', import_uid)], limit=1)

        if not affiliate and import_personal_id:
            affiliate = affiliate_model.search([('personal_id', '=', import_personal_id)], limit=1)

        if not affiliate and import_vat:
            affiliate = affiliate_model.search([('vat', '=', import_vat)], limit=1)

        if not affiliate and import_name:
            affiliate = affiliate_model.search([('name', '=', import_name)], limit=1)

        if not affiliate:
            conf = self.env['affiliation.affiliation_configuration'].search([], limit=1)
            can_create = bool(conf and conf.create_user_from_contribution)
            if not can_create:
                raise ValidationError(_(
                    "Affiliate not found for contribution import. "
                    "Enable 'Create user on contribution import' in affiliation configuration "
                    "or import with an existing affiliate."
                ))

            if not import_uid:
                raise ValidationError(_(
                    "Missing import_uid. It is required to create affiliates from contributions import."
                ))

            affiliate_vals = {
                'uid': import_uid,
                'state': 'new',
                'name': import_name or import_uid,
            }
            if import_vat:
                affiliate_vals['vat'] = import_vat
            if import_personal_id:
                affiliate_vals['personal_id'] = import_personal_id

            affiliate = affiliate_model.create(affiliate_vals)

        vals['affiliate_id'] = affiliate.id
        self._clean_data_affiliate(vals)
        return vals
