# -*- coding: utf-8 -*-
from openerp import models, fields, api

class Requisiciones(models.Model):
    _inherit = 'itsa.planeacion.requisiciones'

class RequisicionesDet(models.Model):
    _inherit = 'itsa.planeacion.requisiciones_det'

class Departamentos(models.Model):
    _inherit = 'itsa.base.deptos'

class itsa_rh_empleados(models.Model):
    _inherit = 'itsa.rh.empleados'

class Entregaproductos(models.Model):
    _name = 'materiales.entregaproductos'
    
    STATUS_SELECTION = [
        ('creado', 'Creado'),
        ('aplicado', 'Aplicado'),
        ('cancelado', 'Cancelado'),
    ]

    name = fields.Char(string='Folio', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('folioEntrega'))
    req_ids = fields.Many2one('itsa.planeacion.requisiciones', string='Requisiciones')  # Campo Many2many para requisiciones
    responsable = fields.Char(string='Responsable de resguardo', compute='_compute_responsable', store=True)    
    fecha = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, readonly=True)
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creado')  # Estado de la entrega
    departamento_id = fields.Many2one('itsa.base.deptos', string='Departamento de asignacion')
    ubicacion = fields.Char(string='Ubicación origen', default='RECURSOS DE MATERIALES Y SERVICIOS', readonly=True)
    detalle_ids = fields.One2many('materiales.detalleentrega', 'entregaproductos_id', string='Detalle recepción')
    

    # @api.model
    # def create(self, vals):
    #     # Crear el registro de Entregaproductos
    #     record = super(Entregaproductos, self).create(vals)

    #     # Buscar todas las compras con estado 'recibido'
    #     compras_recibidas = self.env['materiales.comprados'].search([('status', '=', 'recibido')])

    #     # Obtener las requisiciones de esas compras
    #     requisiciones_recibidas = compras_recibidas.mapped('requisicion_ids')

    #     # Asignar solo las requisiciones de compras 'recibidas' al campo req_ids
    #     record.write({'req_ids': [(6, 0, requisiciones_recibidas.ids)]})

    #     return record
        
    @api.multi
    def action_aplicar(self):
        # Cambiar el estado de la entrega a 'aplicado'
        self.write({'status': 'aplicado'})
    
    @api.multi
    def action_cancelar(self):
        # Cambiar el estado de la entrega a 'cancelado'
        self.write({'status': 'cancelado'})

    @api.onchange('departamento_id')
    def _onchange_departamento_id(self):
        if self.departamento_id:
            self.responsable = self.departamento_id.jefe.name
        else:
            self.responsable = ''
            
    @api.depends('departamento_id')
    def _compute_responsable(self):
        for record in self:
            if record.departamento_id:
                jefe_name = record.departamento_id.jefe.name
                # Actualizamos el valor de responsable sin disparar el write
                record.update({'responsable': jefe_name})
            else:
                record.update({'responsable': ''})

    @api.multi
    def write(self, vals):
        # Evitar que se compute el responsable al escribir si ya está presente en los valores
        if 'responsable' not in vals:
            self._compute_responsable()
        return super(Entregaproductos, self).write(vals)

    
    @api.model
    def create(self, vals):
        record = super(Entregaproductos, self).create(vals)
        record._compute_responsable()
        return record

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('Folioentregaproductos')
        return super(Entregaproductos, self).create(vals)

    @api.multi
    def action_aplicar(self):
        self.write({'status': 'aplicado'})

    @api.model
    def create(self, vals):
        # Crear el registro de Entregaproductos
        record = super(Entregaproductos, self).create(vals)

        # Buscamos las compras con estado 'recibido' y obtenemos sus requisiciones
        compras_recibidas = self.env['materiales.comprados'].search([('status', '=', 'recibido')])

        # Asignamos las requisiciones de las compras con estado 'recibido' al campo req_ids
        requisiciones = compras_recibidas.mapped('requisicion_ids')
        record.write({'req_ids': requisiciones})

        return record
    
class Detalleentrega(models.Model):
    _name = 'materiales.detalleentrega'

    entregaproductos_id = fields.Many2one('materiales.entregaproductos', string='Entrega')
    producto_id = fields.Many2one('materiales.productos', string='Producto')
    #cantidad = fields.Integer(string='Cantidad')
    ubicacion_id = fields.Many2one("materiales.ubicaciones",string='Clave ubicacion destino')
    
    ubicacion_destino = fields.Char(string='Ubicación destino')
    edificio = fields.Char(string='Edificio')
    area = fields.Char(string='Área')
    cantidad = fields.Selection(selection='_get_rango_cantidad', string='Cantidad')
    
    @api.onchange('ubicacion_id')
    def _onchange_ubicacion_id(self):
        if self.ubicacion_id:
            self.ubicacion_destino = self.ubicacion_id.Departamento
            self.edificio = self.ubicacion_id.Edificio
            self.area = self.ubicacion_id.Area
        else:
            self.ubicacion_destino = ''
            self.edificio = ''
            self.area = ''
    
    @api.model
    def _get_rango_cantidad(self):
        # Este método genera una lista de tuplas con números del 1 al 20
        return [(str(num), str(num)) for num in range(1, 500)]
    