# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Requisiciones(models.Model):
    _inherit = 'itsa.planeacion.requisiciones'
    
class Requisiciones_det(models.Model):
    _inherit = 'itsa.planeacion.requisiciones_det'


class Compras(models.Model):
    _name = 'materiales.comprados'

    STATUS_SELECTION = [
        ('creado', 'Creado'),
        ('pedido', 'Pedido'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado'),
    ]

    name = fields.Char(string='Folio', readonly=True)
    fecha = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, readonly=True)
    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor', required=True)
    requisicion_id = fields.Many2one('itsa.planeacion.requisiciones', string='Requisición', required=True)
    requisiciones_det = fields.Many2many('itsa.planeacion.requisiciones_det', 'compras_det_requisicion_det', 'com_id', 'req_id', string='Detalles de Requisición')
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creado')

    total = fields.Float(string='Total estimado', compute='_compute_costo_estimado', store=True)
    totalr = fields.Float(string='Total real', compute='_compute_total', store=True)

    @api.depends('requisiciones_det.importe')
    def _compute_costo_estimado(self):
        for compra in self:
            total = sum(detalle.importe for detalle in compra.requisiciones_det)
            compra.total = total

    @api.depends('requisiciones_det.importe_real')
    def _compute_total(self):
        for compra in self:
            totalr = sum(detalle.importe_real for detalle in compra.requisiciones_det)
            compra.totalr = totalr

    @api.multi
    def action_confirm(self):
        self.write({'status': 'pedido'})

    @api.multi
    def action_receive(self):
        self.write({'status': 'recibido'})

    @api.multi
    def action_cancel(self):
        self.write({'status': 'cancelado'})
            
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('Foliocompras')
        compra = super(Compras, self).create(vals)
        #compra.copy_requisiciones_to_detalle() ME CREABA DOS REGISTROS EN DETALLE COMPRA
        return compra
    
    compra_detalle_ids = fields.One2many('materiales.comprasdetalle', 'compra_id', string='Detalles de Compra')

    @api.multi
    def copy_requisiciones_to_detalle(self):
        for compra in self:
            detalles = []
            for requisicion_det in compra.requisiciones_det:
                detalle_vals = {
                    'compra_id': compra.id,
                    'req_id': requisicion_det.req_id.id,
                    'producto': requisicion_det.producto_id,
                    'cantidad': requisicion_det.cantidad,
                    'costo': requisicion_det.costo,
                    'importe': requisicion_det.importe,
                    'importe_real': requisicion_det.importe_real,
                }
                detalles.append((0, 0, detalle_vals))
            compra.write({'compra_detalle_ids': detalles})

class ComprasDetalle(models.Model):
    _name = 'materiales.comprasdetalle'

    compra_id = fields.Many2one('materiales.comprados', string='Compra', required=True)
    req_id = fields.Many2one('itsa.planeacion.requisiciones', string='Requisición')
    producto = fields.Char(string='Producto', required=True)
    cantidad = fields.Integer(string='Cantidad', required=True)
    costo = fields.Float(string='Costo Unitario', required=True)
    importe = fields.Float(string='Importe Estimado', required=True)
    importe_real = fields.Float(string='Importe Real', required=True)
