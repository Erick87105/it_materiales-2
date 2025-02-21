# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Areas(models.Model):
    _name = 'itsa.materiales.ubicaciones.areas'
    _rec_name = 'name' # Permite mostrar sus campos como tipo char, para mostrarse desde otro modelo.

    name = fields.Char(string='Area Nueva:', required=True)
    
    _sql_constraints = [('itsa_materiales_ubicaciones_areas', 'unique(name)', 'Esta area ya existe')]

class ubicaciones(models.Model):

    _name = 'itsa.materiales.ubicaciones'
    _rec_name = 'departamento_id'

    name = fields.Char(string='Clave', size=10, required=True)
    departamento_id = fields.Many2one('itsa.base.deptos', string='Departamento', required=True)
    area = fields.Many2one('itsa.materiales.ubicaciones.areas', string='Area', required=True)  
    edificio_id = fields.Many2one('itsa.base.edificios', string='Edificio', required=True)
