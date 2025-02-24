# -*- coding: utf-8 -*-
from openerp import models, fields

class ubicaciones(models.Model):

    _name = 'itsa.materiales.ubicaciones'
    _rec_name = 'departamento_id'

    name = fields.Char(string='Clave', size=10, required=True)
    departamento_id = fields.Many2one('itsa.base.deptos', string='Departamento', required=True)
    # area = fields.Many2one('itsa.materiales.ubicaciones.areas', string='Area', required=True)  
    edificio_id = fields.Many2one('itsa.base.edificios', string='Edificio', required=True)
    
    detalle_ids = fields.One2many('ubicacion.detalle', 'ubicacion_id', string='Detalles de la ubicacion')

class UbicacionDetalle(models.Model):
    _name = 'ubicacion.detalle'

    name = fields.Char(string='Nombre del Area:', required=True)
    ubicacion_id = fields.Many2one('itsa.materiales.ubicaciones', string='Departamento', required=True)
    