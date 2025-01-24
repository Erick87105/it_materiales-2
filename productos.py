# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime

class Marcas(models.Model):
    _name = 'itsa.materiales.productos.marcas'

    name = fields.Char(string='Marca Nueva:', required=True)
    
    _sql_constraints = [('itsa_materiales_marcas_unique_name', 'unique(name)', 'El código debe ser único.')]

class Modelos(models.Model):
    _name = 'itsa.materiales.productos.modelos'

    name = fields.Char(string='Modelo Nuevo:', required=True)
    
    _sql_constraints = [('itsa_materiales_modelos_unique_name', 'unique(name)', 'El código debe ser único.')]

class Productos(models.Model):
    _name = 'itsa.materiales.productos'
    
    _description = 'Productos del Inventario'

    foto = fields.Binary(string='Foto del Producto')
    clave = fields.Char(string='Clave', readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    name = fields.Char(string='Nombre del Producto o Servicio')
    marca = fields.Many2one('itsa.materiales.productos.marcas', string='Marca', required=True)
    modelo = fields.Many2one('itsa.materiales.productos.modelos', string='Modelo', required=True)
    tipo_producto = fields.Selection([
        ('consumible', 'Consumible'),
        ('activo_fijo', 'Activo Fijo'),
        ('servicio', 'Servicio')
    ], string='Tipo de Producto', required=True)  
    serie = fields.Char(string='Identificación de Serie')

    # Cambiamos la selección por relaciones a las tablas de depreciación
<<<<<<< HEAD
    categoria_id = fields.Many2one('depreciacion.categoria.name', string='Categoría', required=True)
    subcategoria_id = fields.Many2one('depreciacion.subcategoria', string='Subcategoría', domain="[('categoria_ids', '=', categoria_ids)]", required=True)
=======
    categoria_id = fields.Many2one('depreciacion.categoria', string='Categoría', required=True)
    subcategoria_id = fields.Many2one('depreciacion.subcategoria', string='Subcategoría', domain="[('categoria_id', '=', categoria_id)]", required=True)
>>>>>>> f3109a844ae8d78e094b7e40588b59c626835774

    cantidad = fields.Integer(string='Stock', default=1)
    anos_vida_util = fields.Integer(string='Años de Vida Útil', readonly=True)
    depreciacion_anual = fields.Float(string='% de Depreciación Anual', readonly=True)
    valor_actual = fields.Float(string='Valor Actual')
    valor_depreciado = fields.Float(string='Valor Depreciado', compute='_compute_valor_depreciado', store=True)

    activo = fields.Boolean(string='Activo')
    estatus = fields.Selection([
        ('bueno', 'Buenas condiciones'),
        ('regular', 'Con algunos detalles'),
        ('malo', 'Malas condiciones')
    ], string='Estado del Producto', required=True)  
    observaciones = fields.Text(string='Observaciones')
    descripcion = fields.Text(string='Descripción')

    @api.model
    def create(self, vals):
        vals['clave'] = self.env['ir.sequence'].next_by_code('claveproducto')
        return super(Productos, self).create(vals)

    @api.depends('valor_actual', 'depreciacion_anual', 'anos_vida_util')
    def _compute_valor_depreciado(self):
        for producto in self:
            if producto.create_date:
                # Convertir create_date a objeto datetime
                try:
                    create_date = datetime.strptime(producto.create_date, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    create_date = datetime.strptime(producto.create_date, '%Y-%m-%d')

                dias_transcurridos = (datetime.now() - create_date).days

                if producto.anos_vida_util > 0:
                    depreciacion_diaria = (producto.depreciacion_anual / 100) * producto.valor_actual / 365
                    depreciacion_acumulada = depreciacion_diaria * dias_transcurridos
                    producto.valor_depreciado = producto.valor_actual - depreciacion_acumulada
                else:
                    producto.valor_depreciado = producto.valor_actual
            else:
                producto.valor_depreciado = producto.valor_actual

    @api.onchange('subcategoria_id')
    def _onchange_subcategoria_id(self):
        """ Actualiza los valores de años de vida útil y depreciación al cambiar la subcategoría. """
        if self.subcategoria_id:
            self.anos_vida_util = self.subcategoria_id.anos_vida_util
            self.depreciacion_anual = self.subcategoria_id.depreciacion_anual
        else:
            self.anos_vida_util = 0
            self.depreciacion_anual = 0
