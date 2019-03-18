from odoo import api, fields, models, _
from datetime import date, datetime, timedelta, timezone, time
import datetime
from odoo.exceptions import UserError, Warning

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    estados = fields.Selection([
            ('recibido','Recibido'),
            ('cobrado', 'Cobrado'),
            ('tercero', 'Entregado a Tercero'),
            ('rechazado', 'Rechazado'),
            ('devuelto', 'Devuelto'),
            ('archivado', 'Archivado'),], string='State', default='recibido',
        )
    
    destinatario = fields.Many2one('res.partner', string='Destinatario' )

    
    @api.multi
    def estados_recibido(self):
        return self.write({'estados': 'recibido'})

    @api.multi
    def estados_cobrado(self):
        return self.write({'estados': 'cobrado'})
    
    @api.multi
    def estados_tercero(self):
        if self.destinatario:
            self.write({'estados': 'tercero'})
        else:
            
            msg = 'Para cambiar al estado ENTREGADO A TERCERO es necesario asignar un destinatario'
            raise UserError(_(msg))
            

    
    @api.multi
    def estados_rechazado(self):
        return self.write({'estados': 'rechazado'})
    
    @api.multi
    def estados_devuelto(self):
        return self.write({'estados': 'devuelto'})
    
    @api.multi
    def estados_archivado(self):
        return self.write({'estados': 'archivado'})
    

    fecha_vencimiento = fields.Date(string='Fecha de vencimiento' , default=date.today()  )
    fecha_vencimiento_tres_dias = fields.Date(string='Fecha Venc. en Tres dias', compute='_fec_ven_tres_dias')
    fecha_vencimiento_ocho_dias = fields.Date(string='Fecha Venc. en Ocho dias', compute='_fec_ven_ocho_dias')
    
    # default=date.today()
    @api.one
    @api.depends('fecha_vencimiento') 
    def _fec_ven_tres_dias(self):
        date_format = "%Y-%m-%d"
        inicio = datetime.datetime.strptime(str(self.fecha_vencimiento ), date_format)
        inicio = inicio + timedelta(days=-3)
        self.fecha_vencimiento_tres_dias = inicio


    @api.one
    @api.depends('fecha_vencimiento')
    def _fec_ven_ocho_dias(self):
        date_format = "%Y-%m-%d"
        inicio = datetime.datetime.strptime(str(self.fecha_vencimiento  ), date_format)
        inicio = inicio + timedelta(days=-8)
        self.fecha_vencimiento_ocho_dias = inicio


