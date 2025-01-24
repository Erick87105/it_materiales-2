# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ItsAPlaneacionRequisiciones(models.Model):
    _name = 'itsa.planeacion.requisiciones'
    
    name = fields.Char(string='Folio', readonly=True)
    fecha_sol = fields.Date(string='Fecha de solicitud')
    utilizar_en = fields.Char(string='Para ser utilizado en')
    req_ids = fields.One2many('itsa.planeacion.requisiciones_det', 'req_id', string='Req ref')
    observaciones = fields.Text(string='Observaciones', readonly=True)
    obsv_admin = fields.Text(string='Observaciones del administrador', readonly=True)
    state = fields.Selection([
        ('cre', 'Creada'),
        ('sol', 'Solicitada'),
        ('val', 'Aprobada'),
        ('aut', 'Autorizada'),
        ('surp', 'Surtida Parcial'),
        ('surc', 'Surtida Completa'),
        ('can', 'Cancelada')
    ], string='Estado', readonly=True, default='cre')
    fuente_fin = fields.Selection([
        ('fede', 'Federal'),
        ('esta', 'Estatal'),
        ('prop', 'Propios')
    ], string='Fuente de financiamiento', default='fede')

    _sql_constraints = [('requisicion_uniq', 'unique(name)', 'La requisición está duplicada')]
     
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('Foliorequisicion')
        return super(ItsAPlaneacionRequisiciones,self).create(vals)
    
class ItsAPlaneacionRequisicionesDet(models.Model):
    _name = 'itsa.planeacion.requisiciones_det'
	
    
    req_id = fields.Many2one('itsa.planeacion.requisiciones', string='Ref. Req', ondelete='cascade')
    cantidad = fields.Integer(string='Cantidad')
    producto_id = fields.Char(string='Descripción del bien o servicio')
    costo = fields.Float(string='Costo unitario ya con IVA')
    importe = fields.Float(string='Costo total estimado', compute='_compute_importe', store=True)
    importe_real = fields.Float(string='Costo real', readonly=True)
    saldo = fields.Float(string='Saldo', compute='_compute_saldo', readonly=True)
    auth_recb = fields.Boolean(string='Recibido', default=False)
    saldo_enpart = fields.Boolean(string='Hay Saldo?', compute='_compute_saldo_enpart', readonly=True)
    state = fields.Selection(related='req_id.state', string='Estado', readonly=True, store=True)

    @api.depends('cantidad', 'costo')
    def _compute_importe(self):
        for rec in self:
            rec.importe = rec.cantidad * rec.costo

    @api.depends('importe', 'importe_real')
    def _compute_saldo(self):
        for rec in self:
            rec.saldo = rec.importe - rec.importe_real

    @api.depends('saldo')
    def _compute_saldo_enpart(self):
        for rec in self:
            rec.saldo_enpart = rec.saldo > 0
