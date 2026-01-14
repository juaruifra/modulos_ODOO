from odoo import models, fields

class PeluqueriaServicio(models.Model):
    _name = 'peluqueria.servicio'
    _description = 'Servicio de Peluquería'

    # Nombre del servicio (por ejemplo: Corte Caballero, Tinte Completo, etc.)
    name = fields.Char(string='Servicio', required=True)

    # Precio base que normalmente se cobra por este servicio
    precio_base = fields.Float(string='Precio Base', required=True)

    # Duración del servicio en horas (ejemplo: 0.5 = 30 minutos)
    duracion = fields.Float(string='Duración (horas)', required=True)

    # Permite desactivar un servicio sin borrarlo (así no se podrá seleccionar en nuevas citas)
    activo = fields.Boolean(default=True)
