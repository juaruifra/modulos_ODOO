from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"  # Extendemos el modelo estándar de usuarios

    # ---------------------------------------------------------
    # Propiedades donde este usuario es el vendedor
    # ---------------------------------------------------------
    # One2many porque:
    #   - Un usuario puede vender muchas propiedades
    #
    # inverse_name = 'seller_id'
    #   - Campo Many2one definido en estate.property
    #
    # domain:
    #   - Solo mostrar propiedades disponibles
    #   - En este módulo, una propiedad está disponible cuando:
    #       state = 'new'
    #
    property_ids = fields.One2many(
        comodel_name="estate.property",   # Modelo relacionado
        inverse_name="seller_id",          # Campo Many2one en estate.property
        string="Propiedades disponibles", # Etiqueta visible
        domain=[("state", "=", "new")],    # Filtro automático
    )
