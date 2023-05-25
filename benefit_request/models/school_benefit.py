# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SchoolBenefit(models.Model):
    _name = 'benefit_request.school_benefit'
    _description = 'School benefit\'s model given by ADIUC'

    benefit_request_id = fields.Many2one(
        comodel_name='benefit_request.benefit_request',
        string='Benefit',
        ondelete='cascade'
    )
    school_benefit_type_id = fields.Many2one(
        comodel_name='benefit_request.school_benefit_type',
        string='Type',
        ondelete='restrict'
    )
    affiliate_child_id = fields.Many2one(
        comodel_name='affiliation.affiliate_child', 
        string='Child',
        ondelete='restrict'
    )
    delivered = fields.Boolean(string='Delivered', default=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Applicant',
        related='benefit_request_id.partner_id',
        ondelete='restrict'
    )
    state = fields.Selection(related="benefit_request_id.state")

    @api.onchange('benefit_request_id','school_benefit_type_id')
    def _onchange_benefit_request(self):
        return self._compute_child_domain()

    def _compute_child_domain(self):
        # res = {'domain' : {'affiliate_child_id' : [('verified', '=', True)],}}
        _affiliated = self.env['affiliation.affiliate'].search([('partner_id','=',self.partner_id.id)])
        _child_ids = []
        if _affiliated:
            __childs = _affiliated.affiliate_child_ids
            for _child in __childs :
                _child_ids.append(_child.id)
        # res['domain']['affiliate_child_id'].append(('id', 'in', _child_ids),)
        res = {'domain' : {'affiliate_child_id' : [('id', 'in', _child_ids)],}}
        return res

    @api.constrains('affiliate_child_id')
    def _check_childs(self):
        for record in self:
            _affiliated = record.env['affiliation.affiliate'].search([('partner_id','=',record.partner_id.id)])
            if not _affiliated:
                break
            __childs = _affiliated.affiliate_child_ids.ids
            if record.affiliate_child_id.id in __childs:
                break
            raise ValidationError(_('The children of school benefit is not child of affiliated')) 

    def name_get(self):
        result = []
        for record in self:
            name = '%s,%s' % (record.partner_id.name, record.school_benefit_type_id.name)        
            result.append((record.id, _("%s")%(name)))
        return result



    
