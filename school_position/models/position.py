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
    dependency_id = fields.Many2one(
        comodel_name='school_position.dependency',
        string='Dependency',
        ondelete='restrict'
    )
    tag_ids = fields.Many2many(
        comodel_name='school_position.tag',
        relation='school_position_tag_affiliate_rel',
        column1='position_id',
        column2='tag_id',
        string='Tags'
    )
    # The next field are to manage the importation like ADIUC way
    # It is needed be stored, because are necessary for the import process
    import_uid = fields.Char(string='Import UID')
    import_personal_id = fields.Char(string='Import Personal ID')

    # Related fields for filters
    uid = fields.Char(related='affiliate_id.uid', store=False)
    personal_id = fields.Char(related='affiliate_id.personal_id', store=False)

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
            if 'tag_ids' in vals:
                vals['tag_ids'] = self._get_tag_for_import(vals['tag_ids'])
            self._clean_affiliate_data(vals)
        # self._compute_affiliate_fields(vals)
        res = super(Position, self).create(vals)
        return res

    def write(self,vals):
        # self._compute_affiliate_fields(vals)
        res = super(Position, self).write(vals)
        return res

    # def _compute_affiliate_fields(self, vals):
    #     if 'affiliate_id' in vals:
    #         affiliate = self.env['affiliation.affiliate'].browse(vals['affiliate_id'])
    #         vals['affiliate_uid'] = affiliate.uid
    #         vals['affiliate_personal_id'] = affiliate.personal_id

    def _get_tag_for_import(self,tags):
        return tags[0][2]

    def _clean_affiliate_data(self, vals):
        vals.pop('import_uid') if 'import_uid' in vals else None
        vals.pop('import_personal_id') if 'personal_id' in vals else None
            
