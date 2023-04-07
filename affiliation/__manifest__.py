# -*- coding: utf-8 -*-
{
    'name': "Afiliaciones",

    'summary': """
        Módulo de gestion de gremial de afiliados""",

    'description': """
        Módulo dirigido a la gestión de afiliados gremiales
    """,

    'author': "Geneos",
    'website': "http://www.geneos.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/affiliation_security.xml',
        'security/ir.model.access.csv',
        'views/affiliate_views.xml',
        'views/affiliate_child_views.xml',
        'views/affiliate_state_views.xml',
        'views/affiliation_period_views.xml',
        'views/menu.xml', # should be the last, ever
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
