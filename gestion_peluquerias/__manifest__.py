# -*- coding: utf-8 -*-
{
    # Nombre del módulo (es el que se ve en Odoo)
    'name': 'Gestión de Peluquerías',

    # Versión del módulo
    'version': '1.0',

    # Categoría en el menú de aplicaciones
    'category': 'Services',

    # Resumen corto
    'summary': 'Gestión de citas para peluquerías',

    # Descripción larga del módulo
    'description': """
Módulo para la gestión de una peluquería.
Permite gestionar servicios, estilistas y citas,
calculando automáticamente tiempos y precios.
    """,

    # Autor del módulo
    'author': 'Juan Antonio Ruiz Francés',

    # Módulos de los que depende este módulo
    'depends': ['base'],

    # Archivos de datos que se cargan al instalar el módulo
    'data': [

        # Antes que nada la seguridad
        'security/ir.model.access.csv',

        # Secuencias
        'data/peluqueria_sequence.xml',

        # Ahora las vistas
        'views/peluqueria_servicio_views.xml',
        'views/peluqueria_estilista_views.xml',
        'views/peluqueria_cita_views.xml',
        'views/peluqueria_res_partner_views.xml',
        'views/peluqueria_horario_views.xml',

        # Después el menú
        'views/peluqueria_menu.xml', 

    ],

    # Indica que el módulo es instalable
    'installable': True,

    # Indica que no es una aplicación independiente
    'application': True,
}


