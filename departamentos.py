# -*- coding: utf-8 -*-
from openerp import models, fields

class Departamento(models.Model):
    _name = 'materiales.departamento'
    
    departamento_id = fields.Char(string='ID de Departamento', required=True)
    nombre_departamento = fields.Char(string='Nombre del Departamento', required=True)
    titular = fields.Char(string='Titular', required=True)
    correo = fields.Char(string='Correo', required=True)
