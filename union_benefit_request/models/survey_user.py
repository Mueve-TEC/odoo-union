# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    benefit_request_id = fields.Many2one(
        comodel_name='benefit_request.benefit_request',
        ondelete='set null'
    )

    # @api.model
    # def create(self, vals):
    #     res = super(SurveyUserInput, self).create(vals)
    #     return res

    def _mark_done(self):
        super(SurveyUserInput, self)._mark_done()
        self.create_benefit_from_answers()

    def create_benefit_from_answers(self):
        benefit = self._create_benefit_request()
        if benefit and benefit.id:
            self.benefit_request_id = benefit.id
            benefit.survey_user_input_id = self.id
            self._create_school_benefits_from_answers()
        return

    def _create_benefit_request(self):
        dni = self.user_input_line_ids.filtered(lambda a: a.question_id.title == 'DNI')
        legajo = self.user_input_line_ids.filtered(lambda a: a.question_id.title == 'Legajo')
        
        affiliate = self.env['affiliation.affiliate'].search([('personal_id','=',int(dni.value_number))])
        if not affiliate.id:
            affiliate = self.env['affiliation.affiliate'].search([('uid','=',int(legajo.value_number))])
            if not affiliate.id:
                return None
        survey = self.survey_id

        self._clean_old_requests(affiliate, survey)

        values = {
            'request_type_id': survey.request_type_id.id if survey.request_type_id.id else None,
            'responsible': 2,
            'partner_id': affiliate.partner_id.id
        }
        return self.env['benefit_request.benefit_request'].create(values)

    def _clean_old_requests(self, affiliate, survey):
        benefits = self.env['benefit_request.benefit_request'].search([('partner_id','=',affiliate.partner_id.id)])
        benefits = benefits.filtered(lambda b: b.survey_user_input_id.survey_id.id == survey.id)
        for bnf in benefits:
            bnf.unlink()

    def _create_school_benefits_from_answers(self):
        for n in range(1,4):
            answer_dni = self.user_input_line_ids.filtered(lambda a: a.question_id.title == 'DNI hijo '+ str(n))
            answer_solicitud = self.user_input_line_ids.filtered(lambda a: a.question_id.title == 'Solicitud '+ str(n))
        
            if not answer_dni.value_number:
                continue

            child = self.env['affiliation.affiliate_child'].search([('personal_id','=',int(answer_dni.value_number))])
            if not child.id:
                child = self._create_default_child(int(answer_dni.value_number))

            school_benefit_type =  self.env['benefit_request.school_benefit_type'].search([('name','=',answer_solicitud.value_suggested.value)])
            
            school_benef = self.env['benefit_request.school_benefit'].create({
                'benefit_request_id': self.benefit_request_id.id,
                'school_benefit_type_id': school_benefit_type.id,
                'affiliate_child_id': child.id
            })

    def _create_default_child(self, dni):
        parent = self.env['affiliation.affiliate'].search([('partner_id','=',self.benefit_request_id.partner_id.id)])
        return self.env['affiliation.affiliate_child'].create({
            'name': 'Sin nombre',
            'personal_id': dni,
            'affiliate_ids': [(6, 0, [parent.id])]
        })
# class SurveyUserInputLine(models.Model):
#     _inherit = 'survey.user_input_line'

#     @api.model
#     def create(self, vals):
#         res = super(SurveyUserInputLine, self).create(vals)
#         return res