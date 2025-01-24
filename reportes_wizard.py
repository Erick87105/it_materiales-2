# -*- coding: utf-8 -*-
from openerp import models, fields, api

class reportes(models.TransientModel):

    _name = 'it_materiales.reportes_wizard'


    fecha_desde = fields.Date(string='Fecha Desde')
    fecha_hasta = fields.Date(string='Fecha Hasta')

    @api.multi
    def generar_Reporte(self):
        data = {
        'fecha_desde': self.fecha_desde,
        'fecha_hasta': self.fecha_hasta,
        }
        
        return  self.env['report'].get_action(self, 'it_materiales.lista_compras', data=data)
        