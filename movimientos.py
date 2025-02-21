# -*- coding: utf-8 -*-
from openerp import models, fields, api

class Movimientos(models.Model):

    _name = 'movimientos.ubicaciones'

    STATUS_SELECTION = [
        ('creado', 'Creado'),
        ('aplicado', 'Aplicado'),
        ('cancelado', 'Cancelado'),
    ]

    name = fields.Char(string='Folio', readonly=True)
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creado')
    fecha_cambio = fields.Date(string='Fecha de cambio de ubicación', required=True, default=fields.Date.context_today, readonly=True)
    origen_id = fields.Char(
        string='Departamen de Origen',
        compute='_compute_origen_id',  # Campo computado 
    )
    destino_id = fields.Char(
        string='Departamento de Destino', 
        compute='_compute_destino_id',  # Campo computado
    )
    tipo_movimiento = fields.Selection([
        ('reubicacion', 'Reubicación'),
        ('reasignacion', 'Reasignación'),
    ], string='Tipo de movimiento', required=True, default='reasignacion')
    observaciones = fields.Text(string='Observaciones')
    detalle_ids = fields.One2many('movimientos.detalle', 'movimiento_id', string='Detalles del movimiento')

    @api.depends('detalle_ids.departamento_origen')
    def _compute_origen_id(self):
        """Calcula el departamento de origen basado en los detalles del movimiento."""
        for movimiento in self:
            if movimiento.detalle_ids and movimiento.detalle_ids[0].departamento_origen:
                # Obtenemos el nombre del departamento de origen
                movimiento.origen_id = movimiento.detalle_ids[0].departamento_origen.departamento_id.name
            else:
                movimiento.origen_id = ''

    @api.depends('detalle_ids.departamento_destino_id')
    def _compute_destino_id(self):
        """Calcula el departamento de destino basado en los detalles del movimiento."""
        for movimiento in self:
            if movimiento.detalle_ids and movimiento.detalle_ids[0].departamento_destino_id:
                # Obtenemos el nombre del departamento de destino
                movimiento.destino_id = movimiento.detalle_ids[0].departamento_destino_id.departamento_id.name
            else:
                movimiento.destino_id = ''             

    @api.multi
    def action_aplicar(self):

        self.name = self.env['ir.sequence'].next_by_code('Foliomovimientos')

        # Cambiar el estado de la entrega a 'aplicado'
        self.write({'status': 'aplicado'})
    
    @api.multi
    def action_cancelar(self):
        # Cambiar el estado de la entrega a 'cancelado'
        self.write({'status': 'cancelado'})

class MovimientosDetalle(models.Model):
    _name = 'movimientos.detalle'

    movimiento_id = fields.Many2one('movimientos.ubicaciones', string='Movimiento')
    producto_id = fields.Many2one('itsa.materiales.productos', string='Producto', required=True, domain=[('tipo_producto', '=', 'activo_fijo')])
    departamento_origen = fields.Many2one('itsa.materiales.ubicaciones', string='Departamento origen')
    edificio_origen = fields.Char(string='Edificio origen', compute='_compute_edificioyarea_origen')
    area_origen = fields.Char(string='Área origen', compute='_compute_edificioyarea_origen')
    departamento_destino_id = fields.Many2one('itsa.materiales.ubicaciones', string='Departamento destino')
    edificio_destino = fields.Char(string='Edificio destino', compute='_compute_edificioyarea_destino')
    area_destino = fields.Char(string='Área destino', compute='_compute_edificioyarea_destino')
    descripcion = fields.Text(string='Descripción')

    @api.depends('departamento_origen')
    def _compute_edificioyarea_origen(self):
        """Calcula el edificio y el área basados en el departamento seleccionado."""
        for record in self:
            if record.departamento_origen:
                # Asignar el nombre del edificio y el área basados en el departamento
                record.edificio_origen = record.departamento_origen.edificio_id.name
                record.area_origen = record.departamento_origen.area.name
            else:
                record.edificio_origen = ''
                record.area_origen = ''

    @api.depends('departamento_destino_id')
    def _compute_edificioyarea_destino(self):
        """Calcula el edificio y el área basados en el departamento seleccionado."""
        for record in self:
            if record.departamento_destino_id:
                # Asignar el nombre del edificio y el área basados en el departamento
                record.edificio_destino = record.departamento_destino_id.edificio_id.name
                record.area_destino = record.departamento_destino_id.area.name
            else:
                record.edificio_destino = ''
                record.area_destino = ''