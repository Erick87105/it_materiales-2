# -*- coding: utf-8 -*-
from openerp import models, fields

class Puesto(models.Model):
    _name = 'trabajadores.materiales.puesto'

    name = fields.Char(string='Puesto Nuevo:', required=True)
    
    _sql_constraints = [('trabajadores_materiales_puesto', 'unique(name)', 'Esta puesto ya existe')]

class TrabajadoresMateriales(models.Model):
    _name = 'trabajadores.materiales'
    _description = 'Registro de Trabajadores de Materiales'

    name = fields.Char(string='Nombre Completo', required=True)
    employee_id = fields.Char(string='ID del Empleado', required=True)
    departamento_id = fields.Many2one('itsa.base.deptos', string='Departamento', required=True)
    puesto =  fields.Many2one('trabajadores.materiales.puesto', string='Puesto', required=True)
    date_hired = fields.Date(string='Fecha de Contratación')
    active = fields.Boolean(string='Activo', default=True)

