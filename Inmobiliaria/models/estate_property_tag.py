from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Etiqueta de propiedad"
    _order = "name"

    name = fields.Char("Nombre", required=True)