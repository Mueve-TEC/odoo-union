# -*- coding: utf-8 -*-
{
    'name': "Butterlog",

    'summary': """
        Module for log errors, actions and info on Odoo""",

    'description': """
        Module targeted to developers that need log different kind of events or actions on Odoo
    """,

    'author': "Ibrian Gomez Ortiz",
    'website': "http://www.geneos.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/butter_log_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
