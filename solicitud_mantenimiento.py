# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Departamentos(models.Model):
    _inherit = 'itsa.base.deptos'

class itsa_rh_empleados(models.Model):
    _inherit = 'itsa.rh.empleados'
    
    
class SolicitudMantenimiento(models.Model):
    
    _name = 'solicitud.mantenimiento'
    
    _description = 'Solicitud de Mantenimiento Correctivo'

    # Campo para los estados
    state = fields.Selection([
        ('creado', 'Creado'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='creado')

    @api.multi
    def action_recibir(self):
        """Método para cambiar el estado a 'Recibido'"""
        self.state = 'recibido'

    @api.multi
    def action_cancelar(self):
        """Método para cambiar el estado a 'Cancelado'"""
        self.state = 'cancelado'
        
    name = fields.Char(string='Folio', readonly=True)
    tipo_mantenimiento = fields.Many2one('tipo.mantenimiento', string='Tipo de mantenimiento', required=True)
    area_solicitante = fields.Many2one('itsa.base.deptos', string='Área solicitante', required=True)
    fecha_solicitud = fields.Date(string='Fecha de solicitud', default=fields.Date.context_today, readonly=True)
     
    nombre_solicitante = fields.Many2one('itsa.rh.empleados', string='Nombre del solicitante', required=True)
    descripcion = fields.Text()

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('Foliosolicitud')
        return super(SolicitudMantenimiento,self).create(vals)

class TipoMantenimiento(models.Model):
    _name = 'tipo.mantenimiento'
    _description = 'Tipo de Mantenimiento'

    name = fields.Char(string='Nombre', required=True)