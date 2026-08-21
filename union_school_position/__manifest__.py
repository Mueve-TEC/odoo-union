# -*- coding: utf-8 -*-
{
    "name": "Sindicato - Cargos",
    "summary": """
        Módulo para gestionar los cargos.""",
    "author": "Mueve",
    "website": "https://mueve.org.ar/",
    "category": "Union",
    "license": "GPL-3",
    "version": "19.0.1.0.0",
    "depends": ["base", "union_affiliation"],
    "data": [
        "security/school_position_security.xml",
        "security/ir.model.access.csv",
        "views/position_views.xml",
        "views/position_type_views.xml",
        "views/position_character_views.xml",
        "views/affiliation_configuration_view.xml",
        "views/affiliate_views.xml",
        "views/menu.xml",
        "data/demo_data.xml",
    ],
    "installable": True,
}
