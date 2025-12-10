from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de propiedad"
    _order = "name"

    name = fields.Char("Nombre", required=True)
    
