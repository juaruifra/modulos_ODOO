from odoo import api,fields, models
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Propiedades inmbomibiliaria"

    #ordenación id descendente. Los ultimos en ser añadidos se mostrarán los primeros
    _order = "id desc" 

    # Campos de una propiedad
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

    # Relación con tipos: muchas propiedades pueden tener el mismo tipo.
    # Una propiedad solo puede tener un tipo
    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Tipo de propiedad'
    )

    # Relación comprador: muchas propiedades pueden tener el mismo comprador.
    # Una propiedad solo puede tener un comprador
    buyer_id = fields.Many2one(
        'res.partner',
        string='Comprador',
        copy=False
    )

    # Relación usuarios: muchas propiedades pueden tener el mismo vendedor.
    # Una propiedad solo puede tener un vendedor
    seller_id = fields.Many2one(
        'res.users',
        string='Vendedor',
        default=lambda self: self.env.user
    )

    # Relación Etiquetas
    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Etiquetas'
    )

    # Lo que añade la tabla de ofertas: Relación
    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_id',
        string="Ofertas"
    )

    # Area total, calculada automáticamente
    total_area = fields.Integer(
        string="Total Area",
        compute="_compute_total_area",
        readonly=True
    )

    # Cuando se cambia cualquiera de los dos campos, se ejecuta el recálculo
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

    # Acciones para los botones
    # Cancelar
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("No puedes cancelar una propiedad ya vendida.")
            record.state = 'canceled'

    # Vendido
    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("No puedes vender una propiedad cancelada.")
            record.state = 'sold'

    # Comprobación y validaciones de precios
    _sql_constraints = [
        (
            "check_expected_price_positive",
            "CHECK(expected_price > 0)",
            "El precio esperado debe ser mayor que cero.",
        ),
        (
            "check_selling_price_positive",
            "CHECK(selling_price IS NULL OR selling_price >= 0)",
            "El precio de venta debe ser mayor o igual que cero.",
        ),
    ]


    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price_minimum(self):
        for record in self:
            # El precio de venta puede ser 0 (antes de aceptar ofertas)
            if float_is_zero(record.selling_price, precision_rounding=0.01):
                continue

            min_price = record.expected_price * 0.9

            if float_compare(
                record.selling_price,
                min_price,
                precision_rounding=0.01
            ) < 0:
                raise ValidationError(
                    "El precio de venta no puede ser inferior al 90% del precio esperado."
                )
