# -*- coding: utf-8 -*-

from odoo import models, fields, api

es_AR_state_names = {
    'not_affiliated': 'No afiliado',
    'new': 'Nuevo',
    'pending_suscribe': 'Pendiente de alta',
    'affiliated': 'Afiliado',
    'pending_unsuscribe': 'Pendiente de baja',
    'disaffiliated': 'Desafiliado',
    'historical': 'Histórico'
}


class AffiliateState(models.Model):
    _name = 'benefit_request.affiliate_state'
    _description = 'State od affiliate'

    name = fields.Char(string='name', required=True)
    value = fields.Char(string='value', required=True)

# TODO: find a better way to translate affiliate states
    def name_get(self):
        return [(state.id, es_AR_state_names[state.value]) for state in self]
