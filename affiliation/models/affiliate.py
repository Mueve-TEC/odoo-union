# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Affiliate(models.Model):
    _name = 'affiliation.affiliate'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Union affiliate entity'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', ondelete='cascade', required=True)
    uid = fields.Char(string='Affiliate UID', required=True)
    personal_id_type = fields.Selection([
        ('dni', 'DNI'), 
        ('lc', 'LC'), 
        ('le', 'LE'),
        ('pasaporte', 'PASAPORTE'), 
        ('ci', 'CI')],
        string='Personal ID type', default='dni')
    personal_id = fields.Char(string='Personal ID')
    gender = fields.Selection([
        ('female', 'Female'), 
        ('male', 'Male'),
        ('other', 'Other'), 
        ('not_report', 'Not report')],
        string='Gender', default='not_report')
    civil_status = fields.Selection([
        ('single', 'Single'), 
        ('married', 'Married'),
        ('united', 'United'), 
        ('separated', 'Separated'), 
        ('divorced', 'Divorced'), 
        ('widowed', 'Widowed'),
        ('not_report', 'Not report')],
        string='Marital status', default='not_report')
    birth_date = fields.Date(string='Birth date')
    birth_country = fields.Many2one(comodel_name='res.country', string='Birth country')
    affiliate_child_ids = fields.Many2many(
        comodel_name='affiliation.affiliate_child',
        relation='affiliate_affiliate_child',
        column1='affiliate_id',
        column2='affiliate_child_id',
        string='Childs'
    )
    state = fields.Selection(
        selection=lambda self: self._compute_state(),
        string='Affiliate State')
    affiliation_period_ids = fields.One2many(
        comodel_name='affiliation.affiliation_period',
        inverse_name='affiliate_id',
        string='Affiliation periods'
    )

    @api.constrains('uid')
    def _check_uid(self):
        other = self.env['affiliation.affiliate'].search([('uid','=',self.uid)])
        if len(other.ids) > 1 or (other[0].id != self.id):
            raise ValidationError(_('There is already exist an affiliate with the same uid!'))

    def _compute_state(self):
        states = self.env['affiliation.affiliate_state'].search([('enabled','=',True)])
        array = []
        for state in states:
            array.append((state.name,state.name))
        return array

    # def _evaluate_state(self):
    #     periods = self.env['affiliation.affiliation_period'].search(('affiliate_id','=',self.id),('closed','=',False))
    #     if len(periods):
    #         self.state = 'afiliado'
    #         return
    #     self.state = ''

    def action_affiliate(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'affiliation.affiliation_period',
            'views': [[False, 'form']],
            'target': 'new',
            'context': {
                'default_affiliate_id': self.id,
            }
        }

    def action_disaffiliate(self):
        period = self.env['affiliation.affiliation_period'].search([('affiliate_id','=',self.id),('closed','=',False)])
        if not len(period):
            raise ValidationError(_('There is not exist an open period!'))
        period[0].close()

