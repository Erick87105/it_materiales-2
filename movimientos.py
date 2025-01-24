# -*- coding: utf-8 -*-
from openerp import models, fields, api

class Departamentos(models.Model):
    _inherit = 'itsa.base.deptos'

class itsa_rh_empleados(models.Model):
    _inherit = 'itsa.rh.empleados'

class Movimientos(models.Model):
    _name = 'movimientos.ubicaciones'
    STATUS_SELECTION = [
        ('creado', 'Creado'),
        ('aplicado', 'Aplicado'),
        ('cancelado', 'Cancelado'),
    ]
    
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creado')

    name = fields.Char(string='Folio', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('movimientos.ubicaciones'))
    fecha_cambio = fields.Date(string='Fecha de cambio de ubicación', required=True, default=fields.Date.context_today, readonly=True)
    departamento_id = fields.Many2one('itsa.base.deptos', string='Departamento', required=True)
    ubicacion_id = fields.Many2one('materiales.ubicaciones', string='Ubicación', required=True)
    tipo_movimiento = fields.Selection([
        ('reubicacion', 'Reubicación'),
        ('reasignacion', 'Reasignación'),
    ], string='Tipo de movimiento', required=True, default='reasignacion')
    observaciones = fields.Text(string='Observaciones')
    detalle_ids = fields.One2many('movimientos.detalle', 'movimiento_id', string='Movimientos')

    @api.multi
    def action_aplicar(self):
        # Cambiar el estado de la entrega a 'aplicado'
        self.write({'status': 'aplicado'})
    
    @api.multi
    def action_cancelar(self):
        # Cambiar el estado de la entrega a 'cancelado'
        self.write({'status': 'cancelado'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('Foliomovimientos')
        return super(Movimientos, self).create(vals)

class MovimientosDetalle(models.Model):
    _name = 'movimientos.detalle'

    movimiento_id = fields.Many2one('movimientos.ubicaciones', string='Movimiento')
    producto_id = fields.Many2one('materiales.productos', string='Producto', required=True)
    departamento_origen_id = fields.Many2one('itsa.base.deptos', string='Departamento origen')
    edificio_origen = fields.Char(string='Edificio origen')
    area_origen = fields.Char(string='Área origen')
    departamento_destino_id = fields.Many2one('itsa.base.deptos', string='Departamento destino')
    edificio_destino = fields.Char(string='Edificio destino')
    area_destino = fields.Char(string='Área destino')
    nombre = fields.Char(string='Nombre')
    numero_serie = fields.Char(string='Número de serie')
    descripcion = fields.Text(string='Descripción')

    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        if self.producto_id:
            self.nombre = self.producto_id.name
            self.numero_serie = self.producto_id.serie
            self.descripcion = self.producto_id.descripcion
        else:
            self.nombre = ''
            self.numero_serie = ''
            self.descripcion = ''
