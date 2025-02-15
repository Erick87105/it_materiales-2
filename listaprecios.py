# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Listaprecios(models.Model):
    _name = 'materiales.listaprecios'

    fecha = fields.Date(string='Fecha', default=fields.Date.context_today, readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    aplicado = fields.Boolean(string='Aplicado', default=True)
    line_ids = fields.One2many('materiales.listaprecios.line', 'listaprecios_id', string='Detalles de Lista de Precios')
    precio_historial_ids = fields.One2many('materiales.precio.historial', 'listaprecios_id', string='Historial de Precios')

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):
        """Cargar productos del proveedor seleccionado en 'line_ids'."""
        if self.proveedor_id:
            productos = self.env['itsa.materiales.productos'].search([('proveedor_id', '=', self.proveedor_id.id)])
            self.line_ids = [(0, 0, {
                'clave': producto.clave,
                'nombre': producto.name,
                'precio_actual': producto.valor_actual,
                'categoria': producto.categoria_id.name.name,# El primer .name obtiene el objeto relacionado (la categoría en sí), el segundo .name obtiene el nombre de esa categoría.
                'subcategoria': producto.subcategoria_id.name,
            }) for producto in productos]
        else:
            self.line_ids = []

    @api.multi
    def actualizar_precio(self):
        """Actualizar precios de productos y guardar historial de cambios."""
        for line in self.line_ids:
            if line.nuevo_precio and line.nuevo_precio != line.precio_actual:
                producto = self.env['itsa.materiales.productos'].search([('clave', '=', line.clave)], limit=1)
                # Guardar el historial del cambio de precio
                self.env['materiales.precio.historial'].create({
                    'name': producto.name,
                    'precio_anterior': producto.valor_actual,
                    'precio_nuevo': line.nuevo_precio,
                    'fecha_cambio': fields.Date.context_today(self),
                    'listaprecios_id': self.id,
                })
                # Actualizar el valor_actual del producto
                producto.write({'valor_actual': line.nuevo_precio})

                # Actualizar el precio actual en la línea de la lista de precios
                line.write({'precio_actual': line.nuevo_precio})
                # Limpiar el campo de nuevo precio
                line.write({'nuevo_precio': 0.0})
                
        self.aplicado = True

class Detalleprecios(models.Model):
    _name = 'materiales.listaprecios.line'

    listaprecios_id = fields.Many2one('materiales.listaprecios', string='Lista de Precios')
    clave = fields.Char(string='Clave del Producto')
    nombre = fields.Char(string='Producto')
    precio_actual = fields.Float(string='Precio Actual')
    nuevo_precio = fields.Float(string='Nuevo Precio')
    categoria = fields.Char(string='Categoría')
    subcategoria = fields.Char(string='Subcategoría')

    @api.onchange('clave')
    def _onchange_clave(self):
        """Actualizar campos de detalle al seleccionar un producto."""
        if self.clave:
            producto = self.env['itsa.materiales.productos'].search([('clave', '=', self.clave)], limit=1)
            self.nombre = producto.name
            self.precio_actual = producto.valor_actual
            self.categoria = producto.categoria_id.name
            self.subcategoria = producto.subcategoria_id.name

class PrecioHistorial(models.Model):
    _name = 'materiales.precio.historial'
    _description = 'Historial de Cambios de Precio'

    listaprecios_id = fields.Many2one('materiales.listaprecios', string='Lista de Precios')
    name = fields.Char(string='Producto')
    precio_anterior = fields.Float(string='Precio Anterior')
    precio_nuevo = fields.Float(string='Precio Nuevo')
    fecha_cambio = fields.Date(string='Fecha de Cambio')