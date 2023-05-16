# -*- coding: utf-8 -*-
{
    'name': "Cargos",

    'summary': """
        Módulo para gestionar los cargos""",

    'description': """
        Módulo para la gestión de cargos
    """,

    'author': "Geneos",
    'website': "http://www.geneos.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sindicate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','affiliation'],

    # always loaded
    'data': [
        'security/school_position_security.xml',
        'security/ir.model.access.csv',

        'views/position_views.xml',
        'views/position_type_views.xml',
        'views/position_character_views.xml',
        'views/position_dependency_views.xml',
        'views/menu.xml', #Should be the last ever
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
