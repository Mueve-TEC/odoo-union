# -*- coding: utf-8 -*-
{
    'name': "Sindicato - Solicitudes",
    'summary': """
        Módulo para la gestion de solicitudes y beneficios gremiales.""",
    'author': "Mueve",
    'website': "https://github.com/Mueve-TEC",
    'category': 'Union',
    'version': '1.0',
    'license': "AGPL-3",
    'depends': ['base','survey','mail','union_affiliation'],
    'data': [
        'security/benefit_request_security.xml',
        'security/ir.model.access.csv',
        'data/affiliate_states.xml',
        'data/request_groups.xml',
        'data/school_benefit_types.xml',
        'views/survey_user_views.xml',
        'views/benefit_request_views.xml',
        'views/request_type_views.xml',
        'views/school_benefit_type_views.xml',
        'views/school_benefit_views.xml',
        'views/affiliate_views.xml',
        'views/survey_survey_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
}
