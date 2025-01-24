# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime
# libreria que permite saber la similitud de una cadena de textp
from difflib import SequenceMatcher
import difflib
import logging

class Compras(models.Model):
    _inherit = 'itsa.planeacion.requisiciones_det'

_logger = logging.getLogger(__name__)

class Recepcion(models.Model):
    _name = 'materiales.recepcion'
    _inherit = ['mail.thread']

    name = fields.Char(string='Folio', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('Foliorecepciones'))
    fecha = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, readonly=True)
    status = fields.Selection([('creado', 'Creado'), ('aplicado', 'Aplicado'), ('cancelado', 'Cancelado')], string='Estado', default='creado')
    observaciones = fields.Text(string='Observaciones')
    ubicacion_recepcion = fields.Selection([('bodega', 'Bodega Materiales'), ('otros', 'Almacen')], string='Ubicación de Recepción', required=True, default='bodega')
    detalle_ids = fields.One2many('materiales.detallerec', 'recepcion_id', string='Detalles de Recepción')
    compra_ids = fields.Many2many('materiales.comprados', string='Compras', domain="[('status', '=', 'pedido')]")
    # attachment_ids = fields.Many2many('ir.attachment', string='Adjuntos')
    numero_factura = fields.Char(string='Número de Factura')
    detalle_ids3 = fields.One2many('materiales.detalle.recepcion', 'recepcion_id', string='Detalles de Recepción')

    @api.multi
    def action_comparar_catalogo(self):
        """ Método para comparar los productos de la recepción con el catálogo y sincronizar si es necesario. """
        catalogo_model = self.env['catalogo.productos']
        
        for detalle in self.detalle_ids:
            # Buscar el producto en el catálogo por clave o nombre similar
            producto_catalogo = catalogo_model.search([('clave', '=', detalle.producto)], limit=1)
            
            if not producto_catalogo:
                # Crear el producto en el catálogo si no existe
                nuevo_producto = {
                    'clave': detalle.producto,
                    'nombre': detalle.producto,
                    'precio_actual': detalle.costo_estimado,
                    'categoria': detalle.categoria_id.name if detalle.categoria_id else 'Sin categoría',
                    'subcategoria': detalle.subcategoria_id.name if detalle.subcategoria_id else 'Sin subcategoría'
                }
                catalogo_model.create(nuevo_producto)
                _logger.info("Producto '%s' añadido al catálogo.", detalle.producto)
            else:
                # Si existe, actualizar precio y otros datos
                producto_catalogo.write({
                    'precio_actual': detalle.costo_real or detalle.costo_estimado,
                    'categoria': detalle.categoria_id.name if detalle.categoria_id else producto_catalogo.categoria,
                    'subcategoria': detalle.subcategoria_id.name if detalle.subcategoria_id else producto_catalogo.subcategoria
                })
                _logger.info("Producto '%s' actualizado en el catálogo.", detalle.producto)
    
    
    total_costo_real = fields.Float(string='Total Costo Real', compute='_compute_total_costo_real', store=True)

    @api.depends('detalle_ids.costo_real')
    def _compute_total_costo_real(self):
        for record in self:
            record.total_costo_real = sum(detalle.costo_real for detalle in record.detalle_ids)

    @api.multi
    def action_agregar_impuesto(self):
        """ Método para agregar impuesto de IVA al valor real. """
        # Recuperar el valor del IVA desde la tabla 'materiales.parametros'
        param_model = self.env['materiales.parametros']
        iva_str = param_model.get_param('IVA', default='16')  # Suponiendo que el IVA está almacenado como un porcentaje
        try:
            iva = float(iva_str) / 100  # Convertir a decimal
        except (TypeError, ValueError):
            raise ValidationError("El parámetro IVA no es válido. Revísalo en 'materiales.parametros'.")

        # Actualizar cada detalle de recepción agregando el IVA al costo real
        for detalle in self.detalle_ids:
            if detalle.costo_real:  # Verificar que exista un costo real
                detalle.costo_real *= (1 + iva)  # Aumentar el costo real por el IVA
                detalle.write({'costo_real': detalle.costo_real})
                
    @api.multi
    def action_aplicar(self):
        
        """ Método para aplicar la recepción, cambiando su estado y actualizando las compras relacionadas. """
        
        # Validar costos antes de aplicar
        self.validar_costos()
        
        # Cambiar estado de la recepción
        self.write({'status': 'aplicado'})
        
        # Actualiza el estado de la compra relacionada
        if self.compra_ids:
            self.compra_ids.write({'status': 'recibido'})
        
        # Actualizamos el stock de los productos
        for detalle in self.detalle_ids3:  # Iteramos sobre los detalles de la recepción
            # Buscamos el producto correspondiente
            producto = self.env['itsa.materiales.productos'].search([('clave', '=', detalle.clave)], limit=1)
            
            if producto:
                # Si el producto existe, actualizamos su stock
                producto.write({'cantidad': producto.cantidad + detalle.cantidad})
            else:
                # Si el producto no se encuentra, lanzamos un error
                raise ValidationError("No se encontró el producto con clave: {}".format(detalle.clave))
        
        _logger.info("Recepción '%s' aplicada correctamente y el stock ha sido actualizado", self.name)

        return True

    @api.multi
    def action_cancelar(self):

        self.write({'status': 'cancelado'})
        
        # Actualizar estado de compras relacionadas
        if self.compra_ids:
            self.compra_ids.write({'status': 'cancelado'})


    @api.multi
    def action_cargar_detalles(self):

            # Obtenemos los IDs de las requisiciones actualmente seleccionadas
            compras_seleccionadas_ids = self.compra_ids.ids


            for detalle in self.detalle_ids3:
                # Si el detalle no tiene referencia, lo dejamos (NO lo eliminamos)
                if not detalle.compra_id:
                    continue
        
            # Si tiene referencia pero no está en las compras seleccionadas, lo eliminamos
                else:
                    
                    if detalle.compra_id.id not in compras_seleccionadas_ids:
                        detalle.unlink()

            # """Cargar detalles de compra en los detalles de recepción sin duplicados."""
            detalles_existentes = {
                (
                    detalle.producto_id.id or None,
                    detalle.cantidad,
                    round(detalle.costo_estimado, 2),  # Redondear para evitar problemas de precisión
                    detalle.descripcion.strip(),  # Eliminar espacios adicionales
                    detalle.proveedor_id.id
                )
                for detalle in self.detalle_ids3
            }
            
            detalle_data = []  # Lista para nuevos detalles


            for compra in self.compra_ids:
                for detalle in compra.compra_detalle_ids:
                    # Buscar producto similar en base a la descripción
                    producto_similar = self.buscar_producto_similar(detalle.producto)

                    # Creamos una tupla con los valores del detalle
                    detalle_tupla = (
                        producto_similar.id if producto_similar else None,
                        detalle.cantidad,
                        round(detalle.costo_estimado, 2),  # Redondear el costo para evitar duplicados por decimales
                        detalle.producto.strip(),  # Eliminar espacios adicionales en la descripción
                        compra.proveedor_id.id
                    )

                    if detalle_tupla not in detalles_existentes:
                        # Si no existe en los detalles actuales, los agregamos, aqui se agregan los detalles de las compras actuales que estan seleccionadas 
                        detalle_data.append((0, 0, {
                            'compra_id': compra.id,  # Registra la compra asociada
                            'producto_id': producto_similar.id if producto_similar else None,
                            'cantidad': detalle.cantidad,
                            'costo_estimado': detalle.costo_estimado,
                            'costo_real': detalle.importe_real,
                            'proveedor_id': compra.proveedor_id.id,
                            'descripcion': detalle.producto
                        }))
                        detalles_existentes.add(detalle_tupla)  # Lo marcamos como existente

            if detalle_data:
                self.write({'detalle_ids3': detalle_data})  # Actualizamos la lista de detalles
            else:
                _logger.info("No se encontraron nuevos detalles para cargar.")

# Este método se encarga de buscar un producto similar del modelo productos basándose en la descripción de la compra, la cual se pasa como parámetro.
    def buscar_producto_similar(self, descripcion):

        # Obtiene el valor del parámetro 'similitud_cadenas'
        similitud_minima = float(self.env['materiales.parametros'].get_param('similitud_cadenas'))

        # Aquí se busca en el modelo itsa.materiales.productos (el catálogo de productos) todos los registros (search([])). La variable productos contiene la lista de todos los productos.
        productos = self.env['itsa.materiales.productos'].search([])

        for producto in productos:
            similitud = difflib.SequenceMatcher(None, producto.name, descripcion).ratio()
            if similitud >= similitud_minima:  # Coincidencia del 80% o más
                return producto
        return None



    def validar_costos(self):
        """ Validar que los costos reales no superen el umbral permitido respecto al costo estimado. """
        
        # Recuperar el umbral de 'DIFERENCIA_COSTO_PERMITIDA' desde la tabla 'materiales.parametros'
        param_model = self.env['materiales.parametros']
        umbral_str = param_model.get_param('DIFERENCIA_COSTO_PERMITIDA', default='10')  # Valor predeterminado '10'
        
        # Convertir a float y verificar que sea un número válido
        try:
            umbral = float(umbral_str)
            if umbral <= 0:
                raise ValueError("El umbral debe ser mayor a cero.")
        except (TypeError, ValueError):
            raise ValidationError("El parámetro DIFERENCIA_COSTO_PERMITIDA no es válido. Revísalo en 'materiales.parametros'.")
        
        # Validación de costos en detalle_ids
        for detalle in self.detalle_ids:
            # Verificar que costo_estimado y costo_real tengan valores válidos
            if detalle.costo_estimado and detalle.costo_estimado != 0:
                _logger.info(
                    "Validando costos para producto %s: costo_real=%s, costo_estimado=%s, umbral=%s",
                    detalle.producto, detalle.costo_real, detalle.costo_estimado, umbral
                )
                
                # Cálculo de la diferencia en porcentaje
                diferencia = abs(detalle.costo_real - detalle.costo_estimado) / detalle.costo_estimado * 100
                _logger.info("Diferencia calculada para %s: %s%%", detalle.producto, diferencia)
                
                if diferencia > umbral:
                    raise ValidationError(
                        u'El costo real de {0} excede el umbral permitido de {1}%.'.format(detalle.producto, umbral)
                    )
            else:
                _logger.warning(
                    "El producto %s tiene un costo estimado inválido (%s), se omite la validación.",
                    detalle.producto, detalle.costo_estimado
                )
        
        _logger.info("Validación de costos completada correctamente con umbral de %s%%", umbral)


    def registrar_nuevo_producto(self, detalle):
        if not detalle.proveedor_id:
            raise ValidationError("El campo 'Proveedor' es obligatorio para crear un nuevo producto.")
        return {
            'name': detalle.producto,
            'marca': detalle.marca,
            'modelo': detalle.modelo,
            'serie': detalle.serie,
            'categoria_id': detalle.categoria_id.id,
            'subcategoria_id': detalle.subcategoria_id.id,
            'cantidad': detalle.cantidad,
            'valor_actual': detalle.costo_estimado,
            'anos_vida_util': detalle.anos_vida_util,
            'depreciacion_anual': detalle.depreciacion_anual,
            'proveedor_id': detalle.proveedor_id.id,
            'activo': True,
        }

class DetallesRecepcion(models.Model):
    _name = 'materiales.detalle.recepcion'

    recepcion_id = fields.Many2one('materiales.recepcion', string='Recepción', readonly=True)
    compra_id = fields.Many2one('materiales.comprados', string='Compra Asociada', readonly=True)  # Nuevo campo para la compra asociada
    producto_id = fields.Many2one('itsa.materiales.productos', string='Producto', required=True)
    clave = fields.Char(string='Clave del Producto', related='producto_id.clave', readonly=True)
    cantidad = fields.Integer(string='Cantidad', required=True)
    costo_estimado = fields.Float(string='Costo Estimado', required=True)
    costo_real = fields.Float(string='Costo Real', readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    descripcion = fields.Text(required=True)


    @api.onchange('descripcion')
    def _onchange_descripcion(self):

        """Autocompleta el campo producto_id al escribir una descripción."""
        if self.descripcion:  # Verifica si hay una descripción ingresada

            productos = self.env['itsa.materiales.productos'].search([])  # Busca todos los productos en la base de datos

            for producto in productos:

                # Compara la descripción con el nombre del producto usando similaridad
                similitud = SequenceMatcher(None, producto.name, self.descripcion).ratio()

                if similitud >= 0.6:  # Si hay un 60% o más de similitud

                    self.producto_id = producto.id  # Asigna automáticamente el producto
                    return  # Detiene el proceso después de encontrar el primer producto similar

class Detallerec(models.Model):
    _name = 'materiales.detallerec'

    recepcion_id = fields.Many2one('materiales.recepcion', string='Recepción')
    producto = fields.Char(string='Producto')
    marca = fields.Char(string='Marca')
    modelo = fields.Char(string='Modelo')
    serie = fields.Char(string='Serie')
    
    # Quitar el required=True temporalmente
    categoria_id = fields.Many2one('depreciacion.categoria', string='Categoría')
    subcategoria_id = fields.Many2one('depreciacion.subcategoria', string='Subcategoría', domain="[('categoria_id', '=', categoria_id)]")

    cantidad = fields.Integer(string='Cantidad')
    costo_estimado = fields.Float(string='Costo Estimado')
    costo_real = fields.Float(string='Costo Real')
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    anos_vida_util = fields.Integer(string='Años de Vida Útil', compute='_compute_depreciacion', store=True)
    depreciacion_anual = fields.Float(string='Depreciación Anual (%)', compute='_compute_depreciacion', store=True)

    @api.depends('subcategoria_id')
    def _compute_depreciacion(self):
        for record in self:
            if record.subcategoria_id:
                record.anos_vida_util = record.subcategoria_id.anos_vida_util
                record.depreciacion_anual = record.subcategoria_id.depreciacion_anual
            else:
                record.anos_vida_util = 0
                record.depreciacion_anual = 0

    @api.onchange('categoria_id')
    def _onchange_categoria_id(self):
        self.subcategoria_id = False

