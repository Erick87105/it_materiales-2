# -*- coding: utf-8 -*-
from openerp import models, fields

class Categoria(models.Model):
    _name = 'depreciacion.categoria.nueva'

    name = fields.Char(string='Categoria Nueva:', required=True)
    
  # Restricción para evitar duplicados
    _sql_constraints = [
        ('depreciacion_categoria_nueva_unique_name', 'unique(name)', 'Esta categoría ya existe')]
    
class DepreciacionCategoria(models.Model):
    _name = 'depreciacion.categoria'

    name = fields.Many2one('depreciacion.categoria.nueva', string='Categoria')
    
    descripcion = fields.Text(string='Descripcion de la Categoria')
    subcategoria_ids = fields.One2many('depreciacion.subcategoria', 'categoria_id', ondelete='cascade', string='Subcategorias')

class DepreciacionSubcategoria(models.Model):
    _name = 'depreciacion.subcategoria'

    name = fields.Char(string='Nombre de la Subcategoria', required=True)
    descripcion = fields.Text(string='Descripcion de la Subcategoria')
    anos_vida_util = fields.Integer(string='Años de Vida Util', required=True)
    depreciacion_anual = fields.Float(string='Porcentaje de Depreciacion Anual (%)', required=True)
    categoria_id = fields.Many2one('depreciacion.categoria', string='Categoria', ondelete='cascade', required=True)