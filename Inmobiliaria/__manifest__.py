# -*- coding: utf-8 -*-
{
    'name': 'Inmobiliaria',
    'version': '1.0.0',
    'summary': 'Modulo de gestión inmobiliaria',
    'description': '',
    'author': 'JR',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_menu.xml'
    ], 
    'installable': True,
    'application': True,
}

