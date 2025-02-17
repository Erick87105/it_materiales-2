# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Listaprecios(models.Model):
    _name = 'materiales.listaprecios'


    # Definir la variable STATUS_SELECTION antes de usarla
    STATUS_SELECTION = [
        ('creada', 'Creada'),
        ('aplicada', 'Aplicada'),
    ]

    fecha = fields.Date(string='Fecha de Creacion:', default=fields.Date.context_today, readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor:', domain=lambda self: self._get_proveedor_domain(), required=True)
    aplicado = fields.Boolean(string='Aplicado', default=True)
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creada')
    
    
    line_ids = fields.One2many('materiales.listaprecios.line', 'listaprecios_id', string='Detalles de Lista de Precios')
    precio_historial_ids = fields.One2many('materiales.precio.historial', 'listaprecios_id', string='Historial de Precios')


    def _get_proveedor_domain(self):

        """Obtener el dominio para restringir la selección de proveedores."""

        # Buscar proveedores que ya tienen una lista de precios con estado "aplicada"
        listas_aplicadas = self.search([('status', '=', 'aplicada')])

        proveedores_aplicados = listas_aplicadas.mapped('proveedor_id.id')
        
        # Excluir proveedores que ya tienen una lista de precios aplicada
        return [('id', 'not in', proveedores_aplicados)]

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):

        """Cargar productos del proveedor seleccionado."""

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
    def cargar_productos(self):

        for record in self:
            
            # Obtener todos los productos del proveedor
            productos = self.env['itsa.materiales.productos'].search([('proveedor_id', '=', record.proveedor_id.id)])
            
            # Obtener las claves de los productos ya existentes en la lista de precios
            claves_existentes = record.line_ids.mapped('clave')
            
            # Filtrar productos que no están en la lista de precios
            productos_nuevos = productos.filtered(lambda p: p.clave not in claves_existentes)
            
            # Crear líneas para los productos nuevos
            for producto in productos_nuevos:
                self.env['materiales.listaprecios.line'].create({
                    'listaprecios_id': record.id,
                    'clave': producto.clave,
                    'nombre': producto.name,
                    'categoria': producto.categoria_id.name.name if producto.categoria_id.name else '',
                    'subcategoria': producto.subcategoria_id.name if producto.subcategoria_id else '',
                    'precio_actual': producto.valor_actual,
                    'nuevo_precio': 0.0,
                })

    @api.multi
    def actualizar_precio(self):

        """Actualizar precios de productos y guardar historial de cambios."""

        for line in self.line_ids:

            if line.nuevo_precio and line.nuevo_precio != line.precio_actual:

                self.write({'status': 'aplicada'})
                
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

class PrecioHistorial(models.Model):
    _name = 'materiales.precio.historial'
    _description = 'Historial de Cambios de Precio'

    listaprecios_id = fields.Many2one('materiales.listaprecios', string='Lista de Precios')
    name = fields.Char(string='Producto')
    precio_anterior = fields.Float(string='Precio Anterior')
    precio_nuevo = fields.Float(string='Precio Nuevo')
    fecha_cambio = fields.Date(string='Fecha de Cambio')