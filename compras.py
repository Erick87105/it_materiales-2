# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import Warning

class Requisiciones(models.Model):
    _inherit = 'itsa.planeacion.requisiciones'

class RequisicionesDet(models.Model):
    _inherit = 'itsa.planeacion.requisiciones_det'

class Compras(models.Model):
    _name = 'materiales.comprados'
    
    # Definir la variable STATUS_SELECTION antes de usarla
    STATUS_SELECTION = [
        ('creado', 'Creado'),
        ('pedido', 'Pedido'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado'),
    ]

    name = fields.Char(string='Folio', readonly=True)
    fecha = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    requisicion_ids = fields.Many2many('itsa.planeacion.requisiciones', string='Requisiciones')
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creado')

    total = fields.Float(string='Total estimado', compute='_compute_costo_estimado', store=True)
    totalr = fields.Float(string='Total real', compute='_compute_total', store=True)

    compra_detalle_ids = fields.One2many('materiales.comprasdetalle', 'compra_id', string='Detalles de Compra')

    @api.depends('compra_detalle_ids.costo_estimado')
    def _compute_costo_estimado(self):
        for compra in self:
            total = sum(detalle.costo_estimado for detalle in compra.compra_detalle_ids)
            compra.total = total

    @api.depends('compra_detalle_ids.importe_real')
    def _compute_total(self):
        for compra in self:
            totalr = sum(detalle.importe_real for detalle in compra.compra_detalle_ids)
            compra.totalr = totalr

    @api.multi
    def action_confirm(self):
        vals={}
        vals['name'] = self.env['ir.sequence'].next_by_code('Foliocompras')
        self.write({'status': 'pedido'})
        
        if len(self.compra_detalle_ids) == 0:
            raise Warning('No hay requisiciones en la compra, por favor seleccione al menos una')
        if not vals['name']:
            raise Warning('No hay folio')
        self.write(vals)

    @api.multi
    def action_receive(self):
        self.write({'status': 'recibido'})

    @api.multi
    def action_cancel(self):
        self.write({'status': 'cancelado'})


    @api.multi
    def copy_requisiciones_to_detalle(self):
        
        self.ensure_one()


        # Obtenemos los IDs de las requisiciones actualmente seleccionadas
        requisiciones_seleccionadas_ids = self.requisicion_ids.ids


        for detalle in self.compra_detalle_ids:
            # Si el detalle no tiene referencia, lo dejamos (NO lo eliminamos)
            if not detalle.req_id:
                continue
    
        # Si tiene referencia pero no está en las requisiciones seleccionadas, lo eliminamos
            else:
                
                if detalle.req_id.id not in requisiciones_seleccionadas_ids:
                    detalle.unlink()

        # Creamos un diccionario para almacenar productos agrupados por el nombre del producto
        productos_agrupados = {}

        # Recorremos cada requisición seleccionada
        for requisicion in self.requisicion_ids:
            requisicion_detalles = self.env['itsa.planeacion.requisiciones_det'].search([('req_id', '=', requisicion.id)])

            for requisicion_det in requisicion_detalles:

                # Usamos el nombre del producto como clave única
                clave = (requisicion_det.producto_id, requisicion_det.req_id.id)

                # Si el producto ya existe en el diccionario, sumamos cantidad y costo
                if clave in productos_agrupados:
                    productos_agrupados[clave]['cantidad'] += requisicion_det.cantidad
                    productos_agrupados[clave]['costo_estimado'] += requisicion_det.costo
                else:
                    # Si no existe, creamos una nueva entrada en el diccionario
                    productos_agrupados[clave] = {
                        'compra_id': self.id,
                        'req_id': requisicion_det.req_id.id,
                        'producto': requisicion_det.producto_id,
                        'cantidad': requisicion_det.cantidad,
                        'costo_estimado': requisicion_det.costo,
                        'importe_real': requisicion_det.importe_real,
                    }

        # Agregamos los nuevos detalles sin duplicar los existentes
        detalles_existentes = {(detalle.producto, detalle.req_id.id) for detalle in self.compra_detalle_ids if detalle.req_id}
        nuevos_detalles = [
            (0, 0, vals)
            for clave, vals in productos_agrupados.items()
            if clave not in detalles_existentes
        ]

        self.write({'compra_detalle_ids': nuevos_detalles})


class ComprasDetalle(models.Model):

    _name = 'materiales.comprasdetalle'

    compra_id = fields.Many2one('materiales.comprados', string='Compra', required=True)
    req_id = fields.Many2one('itsa.planeacion.requisiciones', string='Ref. Req', readonly=True)
    producto = fields.Char(string='Producto', required=True, readonly=0)
    cantidad = fields.Integer(string='Cantidad', required=True, readonly=0)
    costo_estimado = fields.Float(string='Costo Estimado', required=True)
    importe_real = fields.Float(string='Costo real', readonly=True)

class lista_compras(models.AbstractModel):

    _name = 'report.it_materiales.lista_compras'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('it_materiales.lista_compras')
        fecha_desde = data['fecha_desde']
        fecha_hasta = data['fecha_hasta']

        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')

        domain = [
            ('fecha', '>=', fecha_desde.strftime('%Y-%m-%d')),
            ('fecha', '<=', fecha_hasta.strftime('%Y-%m-%d')),
        ]


        docs = self.env['materiales.comprados'].search(domain)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
        }
        return report_obj.render('it_materiales.lista_compras', docargs)