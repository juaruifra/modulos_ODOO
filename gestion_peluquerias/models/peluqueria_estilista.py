from odoo import models, fields

class PeluqueriaEstilista(models.Model):
    _name = 'peluqueria.estilista'
    _description = 'Estilista'

    # Nombre del estilista
    name = fields.Char(string='Nombre', required=True)

    # Si no está activo, no debería asignársele nuevas citas
    activo = fields.Boolean(default=True)
