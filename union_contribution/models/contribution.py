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

    @api.model
    def create(self, vals):
        # Am I importing data?
        if 'import_file' in self.env.context:
            if 'import_uid' in vals:
                affiliate = self.env['affiliation.affiliate'].search([('uid','=',vals['import_uid'])])
                if len(affiliate.ids):
                    affiliate = affiliate[0]
                else:
                    conf = self.env['affiliation.affiliation_configuration'].browse(1)
                    if conf.create_user_from_contribution:
                        affiliate = {'uid': vals['import_uid'], 'state': 'new'}
                        # Name field should always come when creating the affiliate
                        if 'import_name' in vals:
                            affiliate.update({'name': vals['import_name']})
                        if 'import_vat' in vals:
                            affiliate.update({'vat': vals['import_vat']})
                        if 'import_personal_id' in vals:
                            affiliate.update({'personal_id': vals['import_personal_id']})
                        affiliate = self.env['affiliation.affiliate'].create(affiliate)
                vals['affiliate_id'] = affiliate.id
                self._clean_data_affiliate(vals)
        res = super(AffiliateContribution, self).create(vals)
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
        log = self.env['butterlog.butterlog'].create(log)
        self.env.user.notify_danger(message=(_('There were errors during importation. See the logs!')))


    def name_get(self):
        result = []
        for record in self:
            name = '%s,%s' % (record.affiliate_id.name, record.date.strftime("%Y-%m-%d"))        
            result.append((record.id, _("%s")%(name)))
        return result

    def _clean_data_affiliate(self, vals):
        vals.pop('import_name') if 'import_name' in vals else None
        vals.pop('import_uid') if 'import_uid' in vals else None
        vals.pop('import_vat') if 'import_vat' in vals else None
        vals.pop('import_personal_id') if 'import_personal_id' in vals else None
