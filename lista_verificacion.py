# -*- coding: utf-8 -*-
from openerp import models, fields, api
# import re

class Departamentos(models.Model):
    _inherit = 'itsa.base.deptos'


class itsa_rh_empleados(models.Model):
    _inherit = 'itsa.rh.empleados'


class ListaVerificacion(models.Model):
    _name = 'lista.verificacion'
    _description = 'Lista de Verificación'

    # Cambiamos el campo para usar la clase heredada 'itsa.base.deptos'
    name = fields.Char(string='Folio', readonly=True)
    area_verificacion = fields.Many2one('itsa.base.deptos', string='Área en la que se realiza la verificación', required=True)

    # Cambiamos la referencia de 'res.users' a 'itsa.rh.empleados'
    jefe_area = fields.Char(string='Jefe/a del área que realiza la verificación', required=True, default=lambda self: self._default_jefe_area())

    @api.model
    def _default_jefe_area(self):
        return self.env['materiales.parametros'].get_param('jefe_area_name')
    trabajador_area = fields.Many2one('trabajadores.materiales', string='Trabajador/a del área', required=True)
    
    # Cambiamos la lógica para referenciar correctamente a 'itsa.rh.empleados'
    jefe_area_verificada = fields.Char(compute='_compute_jefe_area_verificada', store=True, string='Jefe/a del área en la que se realiza la verificación', readonly=True)
    
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    detalle_ids = fields.One2many('lista.verificacion.detalle', 'lista_id', string='Verificación de infraestructura y equipo')

    # Onchange method to populate jefe_area_verificada when area_verificacion is selected
    @api.onchange('area_verificacion')
    def _onchange_area_verificacion(self):
        if self.area_verificacion and self.area_verificacion.jefe:
            # Asignamos el nombre del jefe asociado a 'itsa.rh.empleados'
            self.jefe_area_verificada = self._sanitize_field(self.area_verificacion.jefe.name)
        else:
            self.jefe_area_verificada = ''

    # Compute method to store jefe_area_verificada
    @api.depends('area_verificacion')
    def _compute_jefe_area_verificada(self):
        for record in self:
            if record.area_verificacion and record.area_verificacion.jefe:
                jefe_name = self._sanitize_field(record.area_verificacion.jefe.name)
                record.jefe_area_verificada = jefe_name
            else:
                record.jefe_area_verificada = ''

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('Foliolistaverificacion')
        return super(ListaVerificacion, self).create(vals)

    # Helper method to sanitize field inputs
    def _sanitize_field(self, value):
        if not isinstance(value, unicode):
            value = unicode(value, 'utf-8')
        # Remove invalid characters (only printable ASCII and Unicode letters)
        value = re.sub(r'[^\w\s\.,;:!@#\$%\^&\*\(\)\[\]\{\}\-_\+=<>?/~`\'"\\|]+', '', value)
        return value

    # State field with workflow transitions
    state = fields.Selection([
        ('creado', 'Creado'),
        ('verificado', 'Verificado'),
        ('aplicado', 'Aplicado')
    ], string='Estado', default='creado')

    @api.multi
    def action_verificar(self):
        """Change state to 'Verificado'."""
        self.write({'state': 'verificado'})

    @api.multi
    def action_aplicar(self):
        """Change state to 'Aplicado'."""
        self.write({'state': 'aplicado'})


class ListaVerificacionDetalle(models.Model):
    _name = 'lista.verificacion.detalle'
    _description = 'Detalle de la Verificación'

    lista_id = fields.Many2one('lista.verificacion', string='Lista de Verificación', ondelete='cascade', required=True)
    elemento_revisado = fields.Many2one('elemento.revisado', string='Elemento Revisado', required=True)
    hallazgo = fields.Text(string='Hallazgo')
    atendido = fields.Selection([('si', 'Sí'), ('no', 'No')], string='Atendido Inmediatamente', required=True)


class ElementoRevisado(models.Model):
    _name = 'elemento.revisado'
    _description = 'Elemento Revisado'

    name = fields.Char(string='Nombre', required=True)
