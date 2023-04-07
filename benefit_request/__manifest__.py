# -*- coding: utf-8 -*-
{
    'name': "benefit_request",

    'summary': """
        Módulo para la gestion de solicitudes de ADIUC""",

    'description': """
        Módulo para la gestión de solicitudes y bolsones de ADIUC
    """,

    'author': "Geneos",
    'website': "http://www.geneos.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','affiliation'],

    # always loaded
    'data': [
        'security/benefit_request_security.xml',
        'security/ir.model.access.csv',

        'data/affiliate_states.xml',
        'data/request_groups.xml',
        'data/school_benefit_types.xml',

        'views/benefit_request_views.xml',
        'views/request_type_views.xml',
        'views/school_benefit_type_views.xml',
        'views/school_benefit_views.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
