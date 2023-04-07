# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SchoolBenefit(models.Model):
    _name = 'benefit_request.school_benefit'
    _description = 'School benefit\'s model given by ADIUC'

    benefit_request_id = fields.Many2one(
        comodel_name='benefit_request.benefit_request',
        string='Benefit'
    )
    school_benefit_type_id = fields.Many2one(
        comodel_name='benefit_request.school_benefit_type',
        string='Type'
    )
    affiliate_child_id = fields.Many2one(
        comodel_name='affiliation.affiliate_child', 
        string='Child'
    )
    delivered = fields.Boolean(string='Delivered', default=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Applicant',
        related='benefit_request_id.partner_id'
    )

    @api.onchange('benefit_request_id','school_benefit_type_id')
    def _onchange_benefit_request(self):
        return self._compute_child_domain()

    def _compute_child_domain(self):
        res = {'domain' : {'affiliate_child_id' : [('verified', '=', True)],}}
        _affiliated = self.env['affiliation.affiliate'].search([('partner_id','=',self.partner_id.id)])
        _child_ids = []
        if _affiliated:
            __childs = _affiliated.affiliate_child_ids
            for _child in __childs :
                _child_ids.append(_child.id)
        res['domain']['affiliate_child_id'].append(('id', 'in', _child_ids),)
        return res

    @api.constrains('affiliate_child_id')
    def _check_childs(self):
        _affiliated = self.env['affiliation.affiliate'].search([('partner_id','=',self.partner_id.id)])
        if not _affiliated:
            return
        __childs = _affiliated.affiliate_child_ids
        for _child in __childs :
            if _child.id == affiliate_child_id.id:
                return
        raise ValidationError(_('The children of school benefit is not child of affiliated')) 



    