from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


class GestionPorcentaje(models.Model):
    _name = 'gestion.porcentaje'
    _order = "name"

    name = fields.Integer(string='Monto')
    porcentaje = fields.Float(String="Porcentaje de Comisión %")


class ProductPorcentajeLine(models.Model):
    _name = 'product.porcentaje.line'
    _order = "monto"

    name = fields.Char(string='Descripcion')
    product_id = fields.Many2one('product.template', string='Producto', index=True)
    porcentaje_id = fields.Many2one('gestion.porcentaje', string='Porcentaje', required=True)
    monto = fields.Float(String="Porcentaje de Comisión %", required=True)

    @api.onchange('porcentaje_id')
    def _onchange_porcentaje_id(self):
        self.monto = self.porcentaje_id.porcentaje
