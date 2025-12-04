from odoo import fields, models
from datetime import date
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Propiedades inmbomibiliaria"

    active = fields.Boolean('Activo', default=True)

    state = fields.Selection([
        ('new', 'Nuevo'),
        ('offer_received', 'Oferta recibida'),
        ('offer_accepted', 'Oferta aceptada'),
        ('sold', 'Vendido'),
        ('canceled', 'Cancelado'),
    ], string='Estado', required=True, copy=False, default='new')

    name = fields.Char('Nombre', required=True)
    description = fields.Text('Descripción')
    date_availabality = fields.Date('Fecha de disponibilidad', copy=False,default=lambda self: date.today() + relativedelta(months=3))
    expected_price = fields.Float('Precio esperado', required=True)
    selling_price = fields.Float('Precio de venta',readonly=True, copy=False)

    bedrooms = fields.Integer('Dormitorios', default=2)
    living_area = fields.Integer('Área habitable')
    facades = fields.Integer('Fachadas')

    garage = fields.Boolean('Garaje')
    garden = fields.Boolean('Jardín')
    garden_area = fields.Integer('Área del jardín')

    garden_orientation = fields.Selection([
        ('north', 'Norte'),
        ('south', 'Sur'),
        ('east', 'Este'),
        ('west', 'Oeste')
    ], string='Orientación del jardín')