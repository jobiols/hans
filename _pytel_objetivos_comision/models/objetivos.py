from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.model
    def _default_porcentaje_line_ids(self):
        gs = self.env['gestion.porcentaje'].search([])
        return [(0, 0, {'porcentaje_id': i.id, 'monto': i.porcentaje, 'product': self.id}) for i in gs]

        
    porcentaje_line_id = fields.One2many('product.porcentaje.line', 'product_id', string='Linea de Porcentaje', default=_default_porcentaje_line_ids)
    

    @api.model
    def _refund_cleanup_lines(self, lines):
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.items():
                #if name in MAGIC_COLUMNS:
                #    continue
                if name == 'porcentaje_line_id':
                    values[name] = [(6, 0, line[name].ids)]
                else:
                    continue
            result.append((0, 0, values))
        return result

    @api.model
    def create(self, vals):
        result = super(ProductTemplate, self).create(vals)
        vals['porcentaje_line_id'] = result._refund_cleanup_lines(result.porcentaje_line_id)
        return result

    @api.multi
    def hola(self):
        obj_produc = self.env['product.template'].search([])
        for pro in obj_produc:
            obj_comision = self.env['gestion.porcentaje'].search([])
            pro.write({
                'porcentaje_line_id' : [(0, 0, {'porcentaje_id': i.id, 'monto': i.porcentaje, 'product_id': pro.id}) for i in obj_comision],
            })