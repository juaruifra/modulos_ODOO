from odoo import api,fields, models
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
    post_code = fields.Integer('Código postal')
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

    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Tipo de propiedad'
    )

    buyer_id = fields.Many2one(
        'res.partner',
        string='Comprador',
        copy=False
    )

    seller_id = fields.Many2one(
        'res.users',
        string='Vendedor',
        default=lambda self: self.env.user
    )

    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Etiquetas'
    )

    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_id',
        string="Ofertas"
    )
    
    total_area = fields.Integer(
        string="Total Area",
        compute="_compute_total_area",
        readonly=True
    )

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    # Para el campo mejor oferta
    best_price = fields.Float(
        string="Mejor oferta",
        compute="_compute_best_price",
        depends=["offer_ids.price"],
        readonly=True
    )

    #Función que calcula el máximo
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    # Cuando cambia el campo "garden" se reasignan los campos relacionados
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False