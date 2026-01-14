from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = ['res.partner']

    # Número de citas realizadas por el cliente
    citas_realizadas = fields.Integer(
        compute='_compute_citas_realizadas',
        string='Citas Realizadas'
    )

    # Cliente VIP: se marca automáticamente si supera un número de citas realizadas
    is_vip = fields.Boolean(
        compute='_compute_is_vip',
        string='Cliente VIP'
    )

    # Regla: es VIP si tiene más de 5 citas realizadas
    @api.depends('citas_realizadas')
    def _compute_is_vip(self):
        for partner in self:
            partner.is_vip = partner.citas_realizadas > 5

    # Cuenta cuántas citas en estado "realizada" tiene el cliente
    def _compute_citas_realizadas(self):
        for partner in self:
            partner.citas_realizadas = self.env['peluqueria.cita'].search_count([
                ('cliente_id', '=', partner.id),
                ('state', '=', 'realizada')
            ])
