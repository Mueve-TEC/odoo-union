# -*- coding: utf-8 -*-
{
    'name': "Aportes",

    'summary': """
        Módulo de gestion de aportes gremiales""",

    'description': """
        Módulo para gestión de aportes/contribuciones de afiliados gremiales
    """,

    'author': "Mueve",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sindicate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','affiliation','butterlog','import_ignore_error','web_notify'],

    # always loaded
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
        'views/inconsistencies_menu.xml',# Should be the last ever
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': '_post_init_hook',
}
