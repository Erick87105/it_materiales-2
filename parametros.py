# -*- coding: utf-8 -*-
from openerp import models, fields, api

class MaterialesParametros(models.Model):
    _name = 'materiales.parametros'
    
    key = fields.Char('Nombre del Parametro', required=True, index=True)
    value = fields.Char('Valor', required=True)

    @api.model
    def get_param(self, key, default=None):
        param = self.search([('key', '=', key)], limit=1)
        return param.value if param else default

