from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de propiedad"
    _order = "name"

    name = fields.Char("Nombre", required=True)
    
    # El nombre del tipo debe ser único
    _sql_constraints = [
        (
            'estate_property_type_name_unique',
            'UNIQUE(name)',
            'El nombre del tipo de propiedad debe ser único'
        )
    ]
