from odoo import models, fields

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Oferta de propiedad"
    _order = "price desc"

    price = fields.Float("Precio", required=True)

    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string="Estado", copy=False)

    partner_id = fields.Many2one(
        'res.partner',
        string="Cliente",
        required=True
    )

    property_id = fields.Many2one(
        'estate.property',
        string="Propiedad",
        required=True
    )


