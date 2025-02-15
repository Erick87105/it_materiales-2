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

    name = fields.Char(string='Folio', readonly=True)
    req_ids = fields.Many2one('itsa.planeacion.requisiciones', string='Requisiciones') 
    responsable = fields.Char(string='Responsable de resguardo', compute='_compute_responsable')    
    fecha = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, readonly=True)
    status = fields.Selection(STATUS_SELECTION, string='Estado', default='creado')  # Estado de la entrega
    departamento_id = fields.Many2one('itsa.base.deptos', string='Departamento de asignacion')
    ubicacion = fields.Char(string='Ubicación origen', default='RECURSOS DE MATERIALES Y SERVICIOS', readonly=True)
   
    detalle_ids = fields.One2many('materiales.detalleentrega', 'entregaproductos_id', string='Detalles de Entrega')
    

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


    @api.depends('departamento_id')
    def _compute_responsable(self):
        for record in self:
            if record.departamento_id:
                jefe_name = record.departamento_id.jefe.name
                record.update({'responsable': jefe_name})
            else:
                record.update({'responsable': ''})

    @api.model
    def create(self, vals):
        # Crear el registro de Entregaproductos
        vals['name'] = self.env['ir.sequence'].next_by_code('Folioentregaproductos')
        entrega = super(Entregaproductos, self).create(vals)

        # Buscamos las compras con estado 'recibido' y obtenemos sus requisiciones
        reqs = self.env['itsa.planeacion.requisiciones'].search([('state', 'in', ['surp', 'surc'])])
        detalles = []
        for req in reqs:  # Iterar sobre cada requisición
            compras = self.env['materiales.comprasdetalle'].search([
                ('req_id', '=', req.id),
                ('req_id.compra_id.status', '=', 'recibido')
            ])
            for cmpd in compras:
                if cmpd.producto_id and cmpd.cantidad:  # Validar que los campos existan
                    detalles.append({
                        'entregaproductos_id': entrega.id,
                        'producto_id': cmpd.producto_id.id,
                        'cantidad': cmpd.cantidad
                    })

        # Asignamos las requisiciones de las compras con estado 'recibido' al campo req_ids
        if detalles:
            entrega.write({'detalle_ids': [(0, 0, d) for d in detalles]})

        return entrega
    
class Detalleentrega(models.Model):
    _name = 'materiales.detalleentrega'

    entregaproductos_id = fields.Many2one('materiales.entregaproductos', string='Entrega')
    producto_id = fields.Many2one('materiales.productos', string='Producto')
    cantidad = fields.Integer(string='Cantidad')
    destino_id = fields.Many2one('itsa.base.deptos', string='Destino', related='entregaproductos_id.departamento_id', readonly=True)
    ubicacion_id = fields.Many2one("materiales.ubicaciones", string='Clave ubicacion destino')
    
    edificio = fields.Char(string='Edificio')
    area = fields.Char(string='Área')
    # cantidad = fields.Selection(selection='_get_rango_cantidad', string='Cantidad')
    
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
    
    # @api.model
    # def _get_rango_cantidad(self):
    #     # Este método genera una lista de tuplas con números del 1 al 20
    #     return [(str(num), str(num)) for num in range(1, 500)]
    