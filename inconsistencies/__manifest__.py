# -*- coding: utf-8 -*-
{
    'name': "Gestion de inconsistencias",

    'summary': """
        Módulo para la gestión de inconsistencias de aportantes""",

    'description': """
        Módulo para la gestión de inconsistencias de aportantes gremiales
    """,

    'author': "Geneos",
    'website': "http://www.geneos.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sindicate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','affiliation','contribution'],

    # always loaded
    'data': [
        'security/inconsistencies_security.xml',
        'security/ir.model.access.csv',
        'views/query_views.xml',
        'views/result_views.xml',
        'views/menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': '_post_init_hook',
}
