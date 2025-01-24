# -*- coding: utf-8 -*-

from openerp import models, fields

class Proveedor(models.Model):

    _name = 'materiales.proveedor'

# No permite que se repita el nombre de la empresa
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre de la empresa ya existe.')
    ]

    name = fields.Char(string='Nombre de la Empresa', required=True)
    domicilio = fields.Char(string='Domicilio', required=True)
    correo = fields.Char(string='Correo', required=True)
    representante = fields.Char(string='Representante', required=True)
    ciudad = fields.Char(string='Ciudad', required=True)
    telefono = fields.Char(string='Telefono', size=10, required=True)
    rfc = fields.Char(string='RFC', required=True)
