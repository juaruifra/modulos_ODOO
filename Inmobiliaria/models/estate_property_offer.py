from odoo import models, fields, api
from datetime import timedelta, date

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

    # Campos que van a cambiar si cambia cualquiera de los dos. 
    validity = fields.Integer(
        string="Validez (días)",
        default=7
    )

    date_deadline = fields.Date(
        string="Fecha límite",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline"
    )

    
    # Si se cambia uno, se recalcula el otro. Funciones
    @api.depends('validity', 'create_date')
    def _compute_date_deadline(self):
        """date_deadline = create_date + validity"""
        for record in self:
            create = record.create_date.date() if record.create_date else date.today()
            record.date_deadline = create + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        """Si el usuario cambia date_deadline: recalcular validity"""
        for record in self:
            create = record.create_date.date() if record.create_date else date.today()
            if record.date_deadline:
                delta = record.date_deadline - create
                record.validity = delta.days
