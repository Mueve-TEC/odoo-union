# -*- coding: utf-8 -*-
{
    "name": "Sindicato - Aportes",
    "summary": """
        Módulo de gestion de aportes gremiales.""",
    "author": "Mueve",
    "website": "https://mueve.org.ar/",
    "category": "Union",
    "version": "19.0.1.0.0",
    "license": "GPL-3",
    "depends": ["base", "union_affiliation"],
    "data": [
        "security/contribution_security.xml",
        "security/inconsistencies_security.xml",
        "security/ir.model.access.csv",
        "views/contribution_views.xml",
        "views/contribution_code_views.xml",
        "views/affiliation_configuration_view.xml",
        "views/affiliate_views.xml",
        "views/menu.xml",
        "views/query_views.xml",
        "views/result_views.xml",
        "views/inconsistencies_menu.xml",
        "data/demo_data.xml",
    ],
    "post_init_hook": "_post_init_hook",
    "installable": True,
}
