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

    # Este campo trae automáticamente si el cliente es VIP desde su ficha.
    # Es de solo lectura porque el valor se calcula en res.partner.
    cliente_vip = fields.Boolean(
        related='cliente_id.is_vip',
        string='Cliente VIP',
        readonly=True
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

    # Total parcial a pagar por la cita (suma de subtotales de las líneas). Sin aplicar descuentos manuales.
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True
    )

    # Tipo de descuento manual que se aplicará a la cita.
    # - porcentaje: aplica un % sobre el total
    # - importe: resta una cantidad fija
    descuento_tipo = fields.Selection(
        [
            ('porcentaje', 'Porcentaje (%)'),
            ('importe', 'Importe Fijo'),
        ],
        string='Tipo de Descuento',
        default='porcentaje'
    )

    # Valor del descuento introducido por recepción.
    # El significado depende del tipo elegido arriba.
    descuento_valor = fields.Float(
        string='Valor Descuento',
        default=0.0
    )

    # Total final tras aplicar el descuento manual.
    total_final = fields.Float(
        string='Total Final',
        compute='_compute_total_final',
        store=True
    )

    # Notas internas de la cita.
    # Sirve para guardar observaciones rápidas: alergias, preferencias,
    # comentarios del cliente, etc.
    notas = fields.Text(
        string='Notas de la Cita'
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
                'peluqueria.cita' # El código de la secuencia que definimos en data/peluqueria_sequence.xml
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

    # Calcula el total final aplicando el descuento manual.
    @api.depends('total', 'descuento_tipo', 'descuento_valor')
    def _compute_total_final(self):
        for cita in self:
            descuento_aplicado = 0.0

            # Descuento por porcentaje (ejemplo: 10 => 10%)
            if cita.descuento_tipo == 'porcentaje':
                descuento_aplicado = cita.total * (cita.descuento_valor / 100.0)

            # Descuento por importe fijo (ejemplo: 5 => -5 euros)
            if cita.descuento_tipo == 'importe':
                descuento_aplicado = cita.descuento_valor

            # Nunca permitimos que el total final quede en negativo.
            cita.total_final = max(cita.total - descuento_aplicado, 0.0)

    # Validación del descuento manual para evitar valores incoherentes.
    @api.constrains('descuento_tipo', 'descuento_valor')
    def _check_descuento_valido(self):
        for cita in self:
            if cita.descuento_valor < 0:
                raise ValidationError(
                    'El valor del descuento no puede ser negativo.'
                )

            if cita.descuento_tipo == 'porcentaje' and cita.descuento_valor > 100:
                raise ValidationError(
                    'El descuento por porcentaje no puede ser mayor que 100%.'
                )

    # Regla: una cita debe tener al menos un servicio.
    # Incluimos cliente_id en el decorador para que esta validación también
    # se ejecute al crear la cita (cliente_id siempre viene en el alta).
    @api.constrains('cliente_id', 'linea_servicio_ids')
    def _check_cita_con_servicios(self):
        for cita in self:
            if not cita.linea_servicio_ids:
                raise ValidationError(
                    'La cita debe tener al menos una línea de servicio.'
                )

    # Regla: no se puede guardar una cita si se solapa con otra del mismo estilista
    # Importante: ignoramos las citas canceladas
    @api.constrains('fecha_inicio', 'fecha_fin', 'estilista_id', 'state')
    def _check_solapamiento_citas(self):
        for cita in self:
            # Si faltan fechas, no podemos comprobar nada
            if not cita.fecha_inicio or not cita.fecha_fin:
                continue

            # Buscamos citas del mismo estilista que se crucen en el tiempo
            citas_solapadas = self.search([
                ('id', '!=', cita.id), # Ignoramos la propia cita que se está guardando
                ('estilista_id', '=', cita.estilista_id.id),
                ('state', '!=', 'cancelada'),
                #('state', '!=', 'borrador'), # Opcional: si no se quiere que las citas en borrador bloqueen otras
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
        # Esta validación salta al guardar la cita si cambian la fecha
        # o las líneas de servicio.
        for cita in self:
            if not cita.fecha_inicio:
                continue

            # Calcular fecha_fin manualmente (no usar el campo computado)
            # Así evitamos usar un valor antiguo si todavía no se ha recalculado.
            total_horas = sum(cita.linea_servicio_ids.mapped('duracion'))
            fecha_fin_calculada = cita.fecha_inicio + timedelta(hours=total_horas)

            # Obtener zona horaria del usuario
            # Odoo guarda fechas en UTC; convertimos para comparar en hora local real.
            tz = pytz.timezone(self.env.user.tz or 'UTC')
            
            # Localizar a UTC primero
            fecha_inicio_utc = pytz.utc.localize(cita.fecha_inicio)
            fecha_fin_utc = pytz.utc.localize(fecha_fin_calculada)
            
            # Convertir a hora local
            fecha_inicio_local = fecha_inicio_utc.astimezone(tz)
            fecha_fin_local = fecha_fin_utc.astimezone(tz)

            # Obtener el día de la semana
            # weekday(): lunes=0 ... domingo=6
            dia_semana = str(fecha_inicio_local.weekday())

            # Buscar TODOS los horarios de ese día
            # Puede haber más de una franja (ejemplo: mañana y tarde).
            horarios = self.env['peluqueria.horario'].search([
                ('dia_semana', '=', dia_semana),
                ('cerrado', '=', False)
            ])

            if not horarios:
                raise ValidationError('El horario seleccionado no es válido. La peluqueria está cerrada en ese momento.')

            # Convertir hora de la cita a float
            # Ejemplo: 10:30 -> 10.5
            hora_inicio = fecha_inicio_local.hour + fecha_inicio_local.minute / 60
            hora_fin = fecha_fin_local.hour + fecha_fin_local.minute / 60

            # Comprobar si encaja en ALGUNA franja
            # Con que encaje en una franja válida, la cita se acepta.
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

