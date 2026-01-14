from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class PeluqueriaCita(models.Model):
    _name = 'peluqueria.cita'
    _description = 'Cita de Peluquería'
    _order = 'fecha_inicio'

    # Cliente de la cita (se usa el modelo estándar de Odoo: res.partner)
    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True
    )

    # Estilista que realizará la cita
    estilista_id = fields.Many2one(
        'peluqueria.estilista',
        string='Estilista',
        required=True
    )

    # Fecha y hora de inicio de la cita
    fecha_inicio = fields.Datetime(
        string='Fecha Inicio',
        required=True
    )

    # Fecha y hora de fin de la cita
    # Se calcula automáticamente sumando la duración de todas las líneas de servicio
    fecha_fin = fields.Datetime(
        string='Fecha Fin',
        compute='_compute_fecha_fin',
        store=True
    )

    # Líneas de servicios dentro de la cita
    linea_servicio_ids = fields.One2many(
        'peluqueria.cita.linea',
        'cita_id',
        string='Servicios'
    )

    # Total a pagar por la cita (suma de subtotales de las líneas)
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True
    )

    # Estado de la cita
    state = fields.Selection(
        [
            ('borrador', 'Borrador'),
            ('confirmada', 'Confirmada'),
            ('realizada', 'Realizada'),
            ('cancelada', 'Cancelada'),
        ],
        default='borrador',
        string='Estado'
    )

    # Calcula la fecha de fin sumando las duraciones de las líneas
    @api.depends('fecha_inicio', 'linea_servicio_ids.duracion')
    def _compute_fecha_fin(self):
        for cita in self:
            if not cita.fecha_inicio:
                cita.fecha_fin = False
                continue

            # Sumamos las duraciones (en horas) de todas las líneas de servicio
            total_horas = sum(cita.linea_servicio_ids.mapped('duracion'))

            # Sumamos esas horas a la fecha de inicio para obtener la fecha de fin
            cita.fecha_fin = cita.fecha_inicio + timedelta(hours=total_horas)

    # Calcula el total sumando los subtotales de las líneas
    @api.depends('linea_servicio_ids.subtotal')
    def _compute_total(self):
        for cita in self:
            cita.total = sum(cita.linea_servicio_ids.mapped('subtotal'))

    # Regla: no se puede guardar una cita si se solapa con otra del mismo estilista
    # Importante: ignoramos las citas canceladas para que no bloqueen la agenda
    @api.constrains('fecha_inicio', 'fecha_fin', 'estilista_id', 'state')
    def _check_solapamiento_citas(self):
        for cita in self:
            # Si faltan fechas, no podemos comprobar nada
            if not cita.fecha_inicio or not cita.fecha_fin:
                continue

            # Buscamos citas del mismo estilista que se crucen en el tiempo
            citas_solapadas = self.search([
                ('id', '!=', cita.id),
                ('estilista_id', '=', cita.estilista_id.id),
                ('state', '!=', 'cancelada'),
                ('fecha_inicio', '<', cita.fecha_fin),
                ('fecha_fin', '>', cita.fecha_inicio),
            ])

            # Si hay alguna, no dejamos guardar y mostramos un error
            if citas_solapadas:
                raise ValidationError(
                    'El estilista ya tiene una cita asignada en ese horario.'
                )
