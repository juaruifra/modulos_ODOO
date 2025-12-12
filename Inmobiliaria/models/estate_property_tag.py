from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Etiqueta de propiedad"
    _order = "name"

    name = fields.Char("Nombre", required=True)

    _sql_constraints = [
        (
            'estate_property_tag_name_unique',
            'UNIQUE(name)',
            'El nombre del tag de propiedad debe ser único'
        )
    ]