# -*- coding: utf-8 -*-
{
    'name': "Sindicato - Aportes",
    'summary': """
        Módulo de gestion de aportes gremiales.""",
    'author': "Mueve",
    'website': "https://github.com/Mueve-TEC",
    'category': 'Union',
    'version': '1.0',
    "license": "AGPL-3",
    'depends': ['base','union_affiliation','butterlog','import_ignore_error','web_notify'],
    'data': [
        'security/contribution_security.xml',
        'security/inconsistencies_security.xml',
        'security/ir.model.access.csv',
        'views/contribution_views.xml',
        'views/contribution_code_views.xml',
        'views/affiliation_configuration_view.xml',
        'views/affiliate_views.xml',
        'views/menu.xml',
        'views/query_views.xml',
        'views/result_views.xml',
        'views/inconsistencies_menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': '_post_init_hook',
    "installable": True,
}
