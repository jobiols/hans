from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_id','product_uom_qty')
    def _alertas_info_stock(self):
        producto = self.product_id.name
        if producto  != False:
            if self.product_uom_qty != 0:            
                if self.product_id.type == 'product':
                        
                    domain_venta = [
                                ('product_id','=',self.product_id.id),
                                ('state', 'in', ['sale', 'done']),
                                ('move_ids','!=',False),
                        ]
                
                    ventas_producto = self.env['sale.order.line'].search(domain_venta)

                    stock_pendiente = 0
                    for line in ventas_producto:
                        for pick in line.move_ids:
                            if pick.state not in ['draff','done','cancel']:
                                stock_pendiente += pick.product_uom_qty

                    stock_actual = self.product_id.qty_available - stock_pendiente

                    if (stock_actual - self.product_uom_qty) < 0: 
                        producto = self.product_id.name
                        msg = 'El producto ' + str(producto) + ' cuenta con '+ str(stock_actual) +' unidad(es), ud. intenta vender mas de lo disponible. \n Revise si pronto habra reabastecimiento en Info Stock.'
                        if producto  != False:
                            warning = {
                                        'title': 'MENSAJE AL USUARIO',
                                        'message' : msg
                                }
                            return {'warning': warning or '',
                                                                                                    
                                }  
                    return {}

            

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    info_html = fields.Html(string="info", copy=False)

    @api.multi
    def confirmar_sin_entrega(self):
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()        
        })


    @api.onchange('order_line')
    def actualizar_info_stock(self):
        
        table_ini_compra = """      <strong>Basado en compras confirmadas (Consulte al departamento de compras).</strong><br></br>
                                    <table style="width:90%" class="o_list_view table table-condensed table-striped o_list_view_ungrouped" >
                                    <tr style="background: #556f86; color: white;" >
                                        <th>Producto</th>
                                        <th style="width: 90px;" >Por recibir</th> 
                                        <th style="width: 140px;" >Fecha Pronosticada</th>
                                        <th style="width: 90px;" >Origen</th>
                                    </tr>"""

        table_ini_venta = """       <strong>Basado en ventas confirmadas (Consulte detalles al vendedor correspondiente)</strong><br></br>
                                    <table style="width:90%" class="o_list_view table table-condensed table-striped o_list_view_ungrouped" >
                                    <tr style="background: #556f86; color: white;" >
                                        <th>Producto</th>
                                        <th style="width: 115px;" >Stock Fisico</th>
                                        <th style="width: 90px;" >Por entregar</th> 
                                        <th style="width: 118px;" >Stock Disponible</th>   
                                        <th style="width: 100px;" >Origen</th>
                                        <th style="width: 90px;" >Vendedor</th> 
                                    </tr>"""

        table_end = """ </table> """
        info_compra = ''
        info_venta = ''
        self.info_html = ''

    
        if self.order_line:

            for line in reversed(self.order_line):

                domain_compra = [
                            ('product_id','=',line.product_id.id),
                            ('state', 'in', ['purchase', 'done']),
                            ('move_ids','!=',False),
                        ]
                
                domain_venta = [
                            ('product_id','=',line.product_id.id),
                            ('state', 'in', ['sale', 'done']),
                            ('move_ids','!=',False),
                        ]

                compras_producto = self.env['purchase.order.line'].search(domain_compra)
                ventas_producto = self.env['sale.order.line'].search(domain_venta)

                for move in compras_producto:
                    for pick in move.move_ids:
                        if pick.state not in ['draft','done','cancel']:
                            producto = str(pick.product_id.name or '' )
                            cantidad = str(pick.product_uom_qty or '')
                            fechas_previstas = str(pick.date_expected or '' )
                            origen = str(pick.origin or '' )
                           
                      
                            info_compra += '<tr><td>' +producto+ '</td><td>' +cantidad+ '</td><td>' + fechas_previstas + '</td><td>' + origen + '</td></tr>'
            
                
                stockdispo = 0
                porentregar = 0
                info_venta_uni = ''
                producto = ''
                origen = ''
                vendedor = ''
                stockfisico = 0
                for move in ventas_producto:
                    for pick in move.move_ids:
                        if pick.state not in ['draft','done','cancel']:
                            producto = pick.product_id.name or ''
                                                       
                            porentregar += pick.product_uom_qty
                            stockfisico = pick.product_id.qty_available
                            stockdispo = pick.product_id.qty_available - porentregar
                            

                            vendedor = move.salesman_id.name or ''
                            origen += str(pick.origin) +' '
                                       
                if stockdispo == 0 and porentregar == 0 and stockfisico == 0:
                    info_venta_uni = '<tr><td>' +str(line.product_id.name)+ '</td><td>'  +str(line.product_id.qty_available)+   '</td><td>'+str(porentregar)+ '</td><td>' +str(line.product_id.qty_available)+  '</td><td>' + str(origen)+ '</td><td>' + str(vendedor)+  '</td></tr>'
                else:
                    info_venta_uni = '<tr><td>' +str(producto)+ '</td><td>'  +str(stockfisico)+   '</td><td>'+str(porentregar)+ '</td><td>' +str(stockdispo)+  '</td><td>' + str(origen)+ '</td><td>' + str(vendedor)+  '</td></tr>'
            
                info_venta += info_venta_uni
                           
            self.info_html = table_ini_compra + info_compra + table_end + '<br></br>' + table_ini_venta + info_venta + table_end






                   