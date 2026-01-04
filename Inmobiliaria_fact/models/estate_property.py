from odoo import models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = ["estate.property"]

    def action_sold(self):

        # Llamamos primero al comportamiento original
        result = super().action_sold()

        # eamos una factura vacía
        for record in self:
            if not record.buyer_id:
                raise UserError(
                    "No se puede crear una factura sin comprador."
                )

            self.env["account.move"].create({
                # Cliente de la factura: comprador de la propiedad
                "partner_id": record.buyer_id.id,

                # Tipo de movimiento: Factura de cliente
                "move_type": "out_invoice",

                "invoice_line_ids": [
                    
                    # Línea 1: Comisión 6%
                    (0, 0, {
                        "name": "Comisión inmobiliaria (6%)",
                        "quantity": 1,
                        "price_unit": self.selling_price * 0.06,
                    }),

                    # Línea 2: Gastos administrativos fijos
                    (0, 0, {
                        "name": "Gastos administrativos",
                        "quantity": 1,
                        "price_unit": 100.0,
                    }),
                ],
            })

        return result
