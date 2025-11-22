# -*- coding: utf-8 -*-
{
    'name': "Sindicato - Afiliaciones",
    'summary': """
        Módulo de gestion de gremial de afiliados.""",
    'author': "Mueve",
    'website': "https://github.com/Mueve-TEC",
    'category': 'Union',
    'version': '16.0.1.1.3',
    "license": "AGPL-3",
    'depends': ['base', 'mail'],
    'data': [
        'security/affiliation_security.xml',
        'security/ir.model.access.csv',
        'data/affiliation_number_seq.xml',
        'data/affiliation_type_default.xml',
        'wizards/affiliation_number.xml',
        'wizards/workplace_delete_wizard.xml',
        'views/affiliate_views.xml',
        'views/affiliate_child_views.xml',
        'views/affiliate_type_views.xml',
        'views/affiliation_period_views.xml',
        'views/affiliation_configuration_view.xml',
        'views/workplace_views.xml',
        'views/res_partner_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
}
