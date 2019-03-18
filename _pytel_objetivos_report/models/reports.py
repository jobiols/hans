from odoo import models, fields, api, _
import xlwt
import io
import base64
from xlwt import easyxf
import datetime
import calendar
import os
from collections import defaultdict

class ReporteComisiones(models.TransientModel):
    _name = "reporte.comisiones"
    
    @api.model
    def _get_from_date(self):
        mes = datetime.date.today().strftime("%m")
        anio = datetime.date.today().strftime("%Y")
        return "%s-%s-01" % (anio, mes)

    from_date = fields.Date(string='Desde',default=_get_from_date)
    to_date = fields.Date(string='hasta',default=datetime.date.today())
    
    invoice_report_printed = fields.Boolean('Imprimir Reporte')
    invoice_summary_file = fields.Binary('Reporte Comisiones')
    file_name = fields.Char('Reporte')


    @api.multi
    def action_print_comision_summary(self):
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour("gris", 0x21)
        workbook.set_colour_RGB(0x21, 191, 191, 191)

        worksheet_general = workbook.add_sheet('Reporte General')
        worksheet_detallado = workbook.add_sheet('Reporte Detallado')

        periodo_1 = "Comisiones: " + self.from_date +' - '+ self.to_date
        fecha_inicio = self.from_date
        fecha_fin = self.to_date
    
    ####################################    ESTILOS         ###########################################
        titulo_tabla = easyxf('font:height 200; align: horiz center, vert center, wrap yes; font:bold True, name Cambria;border: top_color black, left_color black, right_color black, bottom_color black, left thin,right thin,top thin,bottom thin;') 
        cont_left_izde_arab = easyxf('font:height 190; align: vert center, wrap yes; font:name Cambria;border: left_color black, right_color black, top_color black, bottom_color black, left thin,right thin, top thin,bottom thin;') 
        cont_center_izde_arab = easyxf('font:height 190; align: horiz center; font:name Cambria;border: left_color black, right_color black, top_color black, bottom_color black, left thin,right thin, top thin,bottom thin;') 
        number_1 = easyxf('font:height 190; align: vert center, wrap yes; font:name Cambria; align: horiz right; border: left_color black, right_color black, top_color black, bottom_color black, left thin,right thin, top thin,bottom thin;', num_format_str= "#,##0.00") 
        number_2 = easyxf('font:height 200, bold True; font:name Cambria; align: horiz right;border: left_color black, right_color black, top_color black, bottom_color black, left thin,right thin, top thin,bottom thin;', num_format_str= "#,##0.00") 
        
    ####################################    CABECERAS         ###########################################
        worksheet_general.write(0, 1, periodo_1, easyxf('font:height 280; font:bold True, name Cambria;'))
        worksheet_general.write_merge(1, 1, 1, 3, 'Reporte de Comisiones', easyxf('font:height 360; align: horiz center; font:bold True, name Cambria;'))
        worksheet_general.write(3, 1, 'ITEM', titulo_tabla)
        worksheet_general.write(3, 2, 'VENDEDOR', titulo_tabla)
        worksheet_general.write(3, 3, 'COMISION', titulo_tabla)

        worksheet_general.col(1).width = 2500
        worksheet_general.col(2).width = 12000
        worksheet_general.col(3).width = 3500

        worksheet_detallado.write(0, 1, periodo_1, easyxf('font:height 280; font:bold True, name Cambria;'))
        worksheet_detallado.write_merge(1, 1, 1, 8, 'REPORTE DETALLADO DE COMISIONES', easyxf('font:height 360; align: horiz center; font:bold True, name Cambria;'))
        worksheet_detallado.write_merge(3, 4, 1, 1, 'ITEM', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 2, 2, 'VENDEDOR', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 3, 3, 'PRODUCTO', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 4, 4, 'MONTO VENDIDO', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 5, 5, 'MONTO RECTIFI.', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 6, 6, 'MONTO TOTAL', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 7, 7, 'COMISION', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 8, 8, 'TOTAL', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 9, 9, 'DETALLE VENTAS', titulo_tabla)
        worksheet_detallado.write_merge(3, 4, 10, 10, 'DETALLE RECTIFICATIVAS', titulo_tabla)

        worksheet_detallado.col(1).width = 2500
        worksheet_detallado.col(2).width = 10000
        worksheet_detallado.col(3).width = 14000
        worksheet_detallado.col(4).width = 3500
        worksheet_detallado.col(5).width = 3500
        worksheet_detallado.col(6).width = 3500
        worksheet_detallado.col(7).width = 3500
        worksheet_detallado.col(8).width = 3500
        worksheet_detallado.col(9).width = 8000
        worksheet_detallado.col(10).width = 8000
        worksheet_detallado.row(3).set_style(easyxf('font:height 240;'))
        worksheet_detallado.row(4).set_style(easyxf('font:height 240;'))

    ########################  Consultas  ########################
        obj_empleados = self.env['hr.employee'].search([('active', '=', True)])
        cont_general = 4
        cont_detallado = 5
        item_general = 0
        item_detallado = 0
        for empleado in obj_empleados:
            producto_precio = defaultdict(float)
            producto_nombre = defaultdict(str)
            producto_id = defaultdict(int)
            producto_pre_total = defaultdict(float)
            monto_vendido = defaultdict(float)
            monto_rectificativa = defaultdict(float)
            detalle_venta = defaultdict(str)
            detalle_rectificativa = defaultdict(str)
            ajajaja = ""
            item_general += 1
            comi_total = 0

            obj_factura_rectificativas = self.env['account.invoice'].search([('type', '=', 'out_refund'), ('state', 'in', ['open','paid']),
                                                                             ('date_invoice', '>=', fecha_inicio), ('date_invoice', '<=', fecha_fin),
                                                                             ])

            obj_facturas_ventas = self.env['account.invoice'].search([('date_invoice', '>=', fecha_inicio), ('date_invoice', '<=', fecha_fin),
                                                                     ('type', '=', 'out_invoice'), ('state', 'in', ['open','paid']),
                                                                     ('move_name', '!=', False), ('user_id.id', '=', empleado.user_id.id)])
            for factura in obj_facturas_ventas:
                obje_invoice_line_ids = self.env['account.invoice.line'].search([('invoice_id', '=', factura.id)])

                for line in obje_invoice_line_ids:
                    detalle_venta[line.product_id.product_tmpl_id.id] +=  factura.number + ' | '
                    producto_precio[line.product_id.product_tmpl_id.id] +=  (line.price_subtotal*(1/(line.invoice_id.currency_id.rate or 1)))
                    producto_nombre[line.product_id.product_tmpl_id.id] =  line.product_id.name
                    producto_id[line.product_id.product_tmpl_id.id] =  line.product_id.product_tmpl_id.id
                    producto_pre_total[line.product_id.product_tmpl_id.id] += (line.price_subtotal*(1/(line.invoice_id.currency_id.rate or 1)))
                    monto_vendido[line.product_id.product_tmpl_id.id] += (line.price_subtotal *(1/(line.invoice_id.currency_id.rate or 1)))
        
            for factura in obj_factura_rectificativas:
                obje_factura_inicial = self.env['account.invoice'].search([('number', '=', factura.origin), ('user_id.id', '=', empleado.user_id.id),('state', 'in', ['open','paid'])]) #

                for fac in obje_factura_inicial:
                    obje_rectificativa_invoice_line_ids = self.env['account.invoice.line'].search([('invoice_id.origin', '=', fac.number), ('invoice_id','=',factura.id)]) #
                    for line in obje_rectificativa_invoice_line_ids:
                        detalle_rectificativa[line.product_id.product_tmpl_id.id] +=  factura.number + ' | '
                        producto_precio[line.product_id.product_tmpl_id.id] -=  (line.price_subtotal*(1/(line.invoice_id.currency_id.rate or 1)))
                        producto_nombre[line.product_id.product_tmpl_id.id] =  line.product_id.name
                        producto_id[line.product_id.product_tmpl_id.id] =  line.product_id.product_tmpl_id.id
                        producto_pre_total[line.product_id.product_tmpl_id.id] -= (line.price_subtotal*(1/(line.invoice_id.currency_id.rate or 1)))
                        monto_rectificativa[line.product_id.product_tmpl_id.id] += (line.price_subtotal*(1/(line.invoice_id.currency_id.rate or 1)))
                    
            inicio = cont_detallado
            for i in list(producto_id):
                item_detallado += 1
                aux_comision = 0
                total = producto_pre_total[i]
                multiplo=total/(abs(total) or 1)
                porcen = 0
                aux_total = abs(total)
                aux_anterior = 0
                obj_comisiones = self.env['product.porcentaje.line'].search([('product_id.id', '=', producto_id[i])])
                comisiones_porcen = defaultdict(float)
                comisiones_monto = defaultdict(int)
                for com in obj_comisiones:
                    if abs(total) >= com.porcentaje_id.name:
                        aux_total -= (com.porcentaje_id.name-aux_anterior)
                        porcen = porcen + ((com.porcentaje_id.name-aux_anterior)*com.monto/100)
                        aux_anterior = com.porcentaje_id.name
                        aux_comision = com.monto
                    elif abs(total)<com.porcentaje_id.name and abs(total)>=aux_anterior:
                        porcen = porcen + (aux_total*com.monto/100)
                        aux_total -= (com.porcentaje_id.name-aux_anterior)
                        aux_comision = com.monto
                        aux_anterior = com.porcentaje_id.name
                if  aux_total >0:
                    porcen = porcen +(aux_total*aux_comision/100)
                
                comi_total += porcen*multiplo

                worksheet_detallado.write(cont_detallado, 1, str(item_detallado).zfill(2), cont_center_izde_arab) #TIPO DE TABLA (2)
                worksheet_detallado.write(cont_detallado, 2, empleado.user_id.name, cont_left_izde_arab) #TIPO DE TABLA (2)
                worksheet_detallado.write(cont_detallado, 3, producto_nombre[i], cont_left_izde_arab) #TIPO DE TABLA (2)
                worksheet_detallado.write(cont_detallado, 4, monto_vendido[i], number_1) 
                worksheet_detallado.write(cont_detallado, 5, monto_rectificativa[i], number_1)
                worksheet_detallado.write(cont_detallado, 6, total, number_1)
                worksheet_detallado.write(cont_detallado, 7, porcen*multiplo, number_1)
                worksheet_detallado.write(cont_detallado, 9,  detalle_venta[i], cont_left_izde_arab)
                worksheet_detallado.write(cont_detallado, 10,  detalle_rectificativa[i], cont_left_izde_arab)
                cont_detallado += 1
            fin = cont_detallado -1
            if inicio<=fin:
                worksheet_detallado.write_merge(inicio, fin, 8, 8, comi_total, number_1)
                #worksheet_detallado.write_merge(inicio, fin, 9, 9, 'VENTAS: ' + detalle_venta[i] + ' \n ' +'RECTIFICATIVAS: '+ detalle_rectificativa[i], cont_left_izde_arab)
            worksheet_general.write(cont_general, 1, str(item_general).zfill(2), cont_center_izde_arab)
            worksheet_general.write(cont_general, 2, empleado.user_id.name, cont_left_izde_arab)
            worksheet_general.write(cont_general, 3, comi_total, number_1)
            cont_general += 1
    ####################################    FINAL    ###################################################
        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.invoice_summary_file = excel_file
        self.file_name =  periodo_1 +'.xls'
        self.invoice_report_printed = True
        fp.close()
        return {
                'view_mode': 'form',
                'res_id': self.id,
                'res_model': 'reporte.comisiones',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
        }