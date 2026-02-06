from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PeluqueriaHorario(models.Model):
    _name = 'peluqueria.horario'
    _description = 'Horario Comercial'
    _order = 'dia_semana, turno' # Ordenamos por día y turno para facilitar la lectura

    # Día de la semana (0=Lunes, 6=Domingo)
    dia_semana = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo'),
    ], string='Día', required=True)

    # Turno: mañana o tarde. Para permitir horarios diferentes en cada turno 
    turno = fields.Selection([
    ('manana', 'Mañana'),
    ('tarde', 'Tarde'),
    ], string='Turno', required=True, default='manana')

    # Hora de apertura (usar widget float_time en la vista)
    hora_apertura = fields.Float(string='Hora Apertura', required=True)

    # Hora de cierre
    hora_cierre = fields.Float(string='Hora Cierre', required=True)

    # Si está cerrado ese día
    cerrado = fields.Boolean(string='Cerrado', default=False)

    # Evitar duplicados del mismo día y turno
    _sql_constraints = [
        ('dia_turno_unico', 'unique(dia_semana, turno)', 'Ya existe un horario para ese día y turno.')
    ]

    # Si está cerrado, no se necesitan horas, pero si no está cerrado, las horas son obligatorias
    # Ademas validamos que la hora de cierre sea posterior a la de apertura
    @api.constrains('hora_apertura', 'hora_cierre', 'cerrado')
    def _check_horas(self):
        for horario in self:

            # Si no está cerrado, las horas deben ser válidas
            if not horario.cerrado:
                if horario.hora_apertura == 0 and horario.hora_cierre == 0:
                    raise ValidationError('Si el día está abierto, debe indicar un horario válido.')

            # Validar que las horas estén en rango válido (0-23)
            if horario.hora_apertura < 0 or horario.hora_apertura > 23:
                raise ValidationError('La hora de apertura debe estar entre 0:00 y 23:59.')
            if horario.hora_cierre < 0 or horario.hora_cierre > 23:
                raise ValidationError('La hora de cierre debe estar entre 0:00 y 23:59.')
            
            # Validar que cierre > apertura (solo si no está cerrado)
            if not horario.cerrado and horario.hora_cierre <= horario.hora_apertura:
                raise ValidationError('La hora de cierre debe ser posterior a la de apertura.')