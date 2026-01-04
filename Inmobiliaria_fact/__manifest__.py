# -*- coding: utf-8 -*-
{
    "name": "Inmobiliaria Fact",
    "version": "1.0.0",
    "summary": "Enlace entre Inmobiliaria (estate) y Facturación (account)",
    "category": "Real Estate",
    "author": "JR",
    "depends": [
        "Inmobiliaria",
        "account",
    ],
    "data": [
        "views/inmobiliaria_fact_menu.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
