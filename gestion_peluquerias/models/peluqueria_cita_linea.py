from odoo import models, fields, api

class PeluqueriaCitaLinea(models.Model):
    _name = 'peluqueria.cita.linea'
    _description = 'Línea de Servicio de la Cita'

    # Cita a la que pertenece esta línea
    # ondelete='cascade' significa: si se borra la cita, se borran sus líneas
    cita_id = fields.Many2one(
        'peluqueria.cita',
        string='Cita',
        required=True,
        ondelete='cascade'
    )

    # Servicio que se va a realizar en esta línea
    servicio_id = fields.Many2one(
        'peluqueria.servicio',
        string='Servicio',
        required=True
    )

    # Duración del servicio para esta cita
    # La copiamos desde el servicio para que quede guardada aunque el servicio cambie en el futuro
    duracion = fields.Float(string='Duración (horas)')

    # Precio del servicio en esta cita
    # Se copia del servicio, pero puede editarse (por ejemplo, si se cobra un extra)
    precio = fields.Float(string='Precio')

    # Subtotal de esta línea
    # Aquí el subtotal es simplemente el precio (no hay cantidad)
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )

    # Cuando se selecciona un servicio, rellenamos automáticamente precio y duración
    @api.onchange('servicio_id')
    def _onchange_servicio_id(self):
        if self.servicio_id:
            self.precio = self.servicio_id.precio_base
            self.duracion = self.servicio_id.duracion

    # Calcula el subtotal de la línea
    @api.depends('precio')
    def _compute_subtotal(self):
        for linea in self:
            linea.subtotal = linea.precio
