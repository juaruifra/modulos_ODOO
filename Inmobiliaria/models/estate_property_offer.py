from odoo import models, fields, api
from datetime import timedelta, date
from odoo.exceptions import UserError

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


    # Funciones para los botones de aceptar y rechazar oferta
    def action_accept(self):
        for offer in self:

            # No permitir aceptar dos ofertas
            if offer.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
                raise UserError("Ya existe una oferta aceptada para esta propiedad.")

            # Cambiar el estado a aceptado
            offer.status = 'accepted'

            #recuperamos la propiedad
            property = offer.property_id

            # Actualizar información en la propiedad
            property.selling_price = offer.price
            property.buyer_id = offer.partner_id
            property.state = 'offer_accepted'

            # Rechazar automáticamente las demás ofertas
            other_offers = property.offer_ids - offer
            other_offers.write({'status': 'refused'})

    def action_refuse(self):
        for offer in self:
            if offer.status == 'accepted':
                raise UserError("No puedes rechazar una oferta que ya ha sido aceptada.")
            offer.status = 'refused'
