from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de propiedad"
    _order = "sequence, name"

    name = fields.Char("Nombre", required=True)
    
    # El nombre del tipo debe ser único
    _sql_constraints = [
        (
            'estate_property_type_name_unique',
            'UNIQUE(name)',
            'El nombre del tipo de propiedad debe ser único'
        )
    ]

    property_ids = fields.One2many(
        'estate.property',
        'property_type_id',
        string='Propiedades'
    )

    sequence = fields.Integer('Secuencia', default=1)

    # Todas las ofertas asociadas a este tipo de propiedad
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_type_id",
        string="Offers",
    )

    
    # Número de ofertas (para el botón estadístico)
    offer_count = fields.Integer(
        string="Offers",
        compute="_compute_offer_count",
    )


    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
