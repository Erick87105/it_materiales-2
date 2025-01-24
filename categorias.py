# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp.exceptions import ValidationError

class DepreciacionCategoria(models.Model):
    _name = 'depreciacion.categoria'

    name = fields.Char(string='Nombre de la Categoria', required=True)
    descripcion = fields.Text(string='Descripcion de la Categoria')
    subcategoria_ids = fields.One2many('depreciacion.subcategoria', 'categoria_id', string='Subcategorias')


class DepreciacionSubcategoria(models.Model):
    _name = 'depreciacion.subcategoria'

    name = fields.Char(string='Nombre de la Subcategoria', required=True)
    descripcion = fields.Text(string='Descripcion de la Subcategoria')
    anos_vida_util = fields.Integer(string='Años de Vida Util', required=True)
    depreciacion_anual = fields.Float(string='Porcentaje de Depreciacion Anual (%)', required=True)
    categoria_id = fields.Many2one('depreciacion.categoria', string='Categoria', ondelete='cascade', required=True)