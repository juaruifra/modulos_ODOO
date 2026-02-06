from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import pytz

class PeluqueriaCita(models.Model):
    _name = 'peluqueria.cita'
    _description = 'Cita de Peluquería'
    _order = 'fecha_inicio'

    # Código automático de la cita
    # Será algo como: CITA/2026/00001
    name = fields.Char(
        string='Código de Cita',
        readonly=True,
        copy=False,
        default='Nueva',
        required=False
    )

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

    # Asigna automáticamente el código de cita al crearla
    @api.model
    def create(self, vals):
        # Si la cita todavía no tiene código, se lo asignamos
        if vals.get('name', 'Nueva') == 'Nueva':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'peluqueria.cita'
            ) or 'Nueva'

        # Llamamos al create original de Odoo
        return super().create(vals)

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

    # Regla: no se puede asignar una cita en una fecha u hora pasada
    @api.constrains('fecha_inicio')
    def _check_fecha_inicio_no_pasada(self):
        # Recorremos las citas que se están guardando
        for cita in self:
            # Si no hay fecha de inicio, no comprobamos nada
            if not cita.fecha_inicio:
                continue

            # Obtenemos la fecha y hora actual
            ahora = fields.Datetime.now()

            # Si la fecha de la cita es anterior a ahora, lanzamos error
            if cita.fecha_inicio < ahora:
                raise ValidationError(
                    'No se puede asignar una cita en una fecha u hora anterior a la actual.'
                )
            


    # Pasa la cita de borrador a confirmada
    def action_confirmar(self):
        for cita in self:
            cita.state = 'confirmada'

    # Pasa la cita a estado realizada
    def action_realizar(self):
        for cita in self:
            cita.state = 'realizada'

    # Cancela la cita
    def action_cancelar(self):
        for cita in self:
            cita.state = 'cancelada'

    # Devuelve la cita a borrador
    # Esto puede ser útil si se ha cometido un error
    def action_volver_borrador(self):
        for cita in self:
            cita.state = 'borrador'

    # Regla: no se puede asignar una cita a un estilista inactivo
    @api.constrains('estilista_id')
    def _check_estilista_activo(self):
        for cita in self:
            # Si no hay estilista asignado, no comprobamos nada
            if not cita.estilista_id:
                continue

            # Si el estilista está inactivo, no permitimos guardar la cita
            if not cita.estilista_id.activo:
                raise ValidationError(
                    'No se puede asignar una cita a un estilista que no está activo.'
                )

    # Validación para asegurar que la cita se asigna dentro del horario comercial      
    @api.constrains('fecha_inicio', 'linea_servicio_ids')
    def _check_horario_comercial(self):
        
        for cita in self:
            if not cita.fecha_inicio:
                continue

            # Calcular fecha_fin manualmente (no usar el campo computado)
            total_horas = sum(cita.linea_servicio_ids.mapped('duracion'))
            fecha_fin_calculada = cita.fecha_inicio + timedelta(hours=total_horas)

            # Obtener zona horaria del usuario
            tz = pytz.timezone(self.env.user.tz or 'UTC')
            
            # Localizar a UTC primero
            fecha_inicio_utc = pytz.utc.localize(cita.fecha_inicio)
            fecha_fin_utc = pytz.utc.localize(fecha_fin_calculada)
            
            # Convertir a hora local
            fecha_inicio_local = fecha_inicio_utc.astimezone(tz)
            fecha_fin_local = fecha_fin_utc.astimezone(tz)

            # Obtener el día de la semana
            dia_semana = str(fecha_inicio_local.weekday())

            # Buscar TODOS los horarios de ese día
            horarios = self.env['peluqueria.horario'].search([
                ('dia_semana', '=', dia_semana),
                ('cerrado', '=', False)
            ])

            if not horarios:
                raise ValidationError('La peluquería está cerrada ese día.')

            # Convertir hora de la cita a float
            hora_inicio = fecha_inicio_local.hour + fecha_inicio_local.minute / 60
            hora_fin = fecha_fin_local.hour + fecha_fin_local.minute / 60

            # Comprobar si encaja en ALGUNA franja
            cita_valida = False
            for horario in horarios:
                if hora_inicio >= horario.hora_apertura and hora_fin <= horario.hora_cierre:
                    cita_valida = True
                    break

            if not cita_valida:
                raise ValidationError('La cita está fuera del horario comercial.')

    # Regla: solo se pueden modificar las citas en estado borrador
    # sobrescribimos el método write para implementar esta regla        
    def write(self, vals):
        for cita in self:
            # Si no está en borrador, solo permitir cambiar el estado
            if cita.state != 'borrador':
                campos_permitidos = {'state'}
                campos_modificados = set(vals.keys())
                if not campos_modificados.issubset(campos_permitidos):
                    raise ValidationError('Solo se puede modificar una cita en estado Borrador.')
        return super().write(vals)

