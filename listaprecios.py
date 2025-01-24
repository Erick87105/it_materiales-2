# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Listaprecios(models.Model):
    _name = 'materiales.listaprecios'

    _sql_constraints = [
        ('proveedor_uniq', 'unique(proveedor_id)', 'Ya existe una lista de precios para este proveedor.')
    ]
    
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today, readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    producto_id = fields.Many2one('materiales.productos', string='Producto')
    aplicado = fields.Boolean(string='Aplicado', default=True)
    line_ids = fields.One2many('materiales.listaprecios.line', 'listaprecios_id', string='Detalles de Lista de Precios')
    precio_historial_ids = fields.One2many('materiales.precio.historial', 'listaprecios_id', string='Historial de Precios')

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):
        """Cargar productos del proveedor seleccionado en 'line_ids'."""
        if self.proveedor_id:
            productos = self.env['materiales.productos'].search([('proveedor_id', '=', self.proveedor_id.id)])
            self.line_ids = [(0, 0, {
                'producto_id': producto.id,
                'clave': producto.clave,
                'nombre': producto.name,
                'precio_actual': producto.valor_actual,
                'categoria': producto.categoria_id.name,
                'subcategoria': producto.subcategoria_id.name,
            }) for producto in productos]
        else:
            self.line_ids = []

    @api.multi
    def actualizar_precio(self):
        """Actualizar precios de productos y guardar historial de cambios."""
        self.ensure_one()
        if not self.aplicado:
            for line in self.line_ids:
                if line.nuevo_precio and line.nuevo_precio != line.precio_actual:
                    producto = line.producto_id
                    # Guardar el historial del cambio de precio
                    self.env['materiales.precio.historial'].create({
                        'producto_id': producto.id,
                        'precio_anterior': producto.valor_actual,
                        'precio_nuevo': line.nuevo_precio,
                        'fecha_cambio': fields.Date.context_today(),
                        'listaprecios_id': self.id,
                    })
                    # Actualizar el valor_actual del producto
                    producto.write({'valor_actual': line.nuevo_precio})
            self.aplicado = True
            self.sync_catalogo()

    @api.model
    def create(self, vals):
        record = super(Listaprecios, self).create(vals)
        record.sync_catalogo()
        return record

    @api.multi
    def write(self, vals):
        res = super(Listaprecios, self).write(vals)
        self.sync_catalogo()
        return res

    @api.multi
    def sync_catalogo(self):
        """Sincronizar productos de 'materiales.productos' con 'catalogo.productos'."""
        catalogo_model = self.env['catalogo.productos']
        productos = self.env['materiales.productos'].search([])
        
        for producto in productos:
            catalogo_producto = catalogo_model.search([('clave', '=', producto.clave)], limit=1)
            if catalogo_producto:
                # Solo actualiza si hay cambios en el producto del catálogo
                if (catalogo_producto.precio_actual != producto.valor_actual or 
                    catalogo_producto.categoria != producto.categoria_id.name or 
                    catalogo_producto.subcategoria != producto.subcategoria_id.name):
                    
                    catalogo_producto.write({
                        'nombre': producto.name,
                        'precio_actual': producto.valor_actual,
                        'categoria': producto.categoria_id.name,
                        'subcategoria': producto.subcategoria_id.name
                    })
                    _logger.info("Producto '%s' actualizado en el catálogo.", producto.name)
            else:
                # Crear producto en catálogo si no existe
                catalogo_model.create({
                    'clave': producto.clave,
                    'nombre': producto.name,
                    'precio_actual': producto.valor_actual,
                    'categoria': producto.categoria_id.name,
                    'subcategoria': producto.subcategoria_id.name
                })
                _logger.info("Producto '%s' añadido al catálogo.", producto.name)


class Detalleprecios(models.Model):
    _name = 'materiales.listaprecios.line'

    listaprecios_id = fields.Many2one('materiales.listaprecios', string='Lista de Precios')
    producto_id = fields.Many2one('materiales.productos', string='Producto')
    clave = fields.Char(string='Clave')
    nombre = fields.Char(string='Nombre')
    precio_actual = fields.Float(string='Precio Actual')
    nuevo_precio = fields.Float(string='Nuevo Precio')
    categoria = fields.Char(string='Categoría')
    subcategoria = fields.Char(string='Subcategoría')

    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        """Actualizar campos de detalle al seleccionar un producto."""
        if self.producto_id:
            self.clave = self.producto_id.clave
            self.nombre = self.producto_id.name
            self.precio_actual = self.producto_id.valor_actual
            self.categoria = self.producto_id.categoria_id.name
            self.subcategoria = self.producto_id.subcategoria_id.name


class CatalogoProductos(models.Model):
    _name = 'catalogo.productos'
    _description = 'Catálogo de Productos'
    _rec_name = 'nombre'

    clave = fields.Char(string='Clave', readonly=True)
    nombre = fields.Char(string='Nombre', readonly=True)
    precio_actual = fields.Float(string='Precio Actual', readonly=True)
    categoria = fields.Char(string='Categoría', readonly=True)
    subcategoria = fields.Char(string='Subcategoría', readonly=True)


class PrecioHistorial(models.Model):
    _name = 'materiales.precio.historial'
    _description = 'Historial de Cambios de Precio'

    listaprecios_id = fields.Many2one('materiales.listaprecios', string='Lista de Precios')
    producto_id = fields.Many2one('materiales.productos', string='Producto')
    precio_anterior = fields.Float(string='Precio Anterior')
    precio_nuevo = fields.Float(string='Precio Nuevo')
    fecha_cambio = fields.Date(string='Fecha de Cambio')
