# -- coding: utf-8 --
from openerp import models, fields

class MaintenanceProgram(models.Model):
    _name = 'materiales.programa'

    semester = fields.Selection([('A', 'Ene/Jun '), ('B', 'Ago/Dic')], string='Semestre', required=True)
    year = fields.Char(string='Año', required=True)
    services = fields.One2many('materiales.service', 'program_id', string='Servicios')
    elaborated_by = fields.Char(string='Elaborado por', required=True)
    approved_by = fields.Char(string='Aprobado por', required=True)
    date_elaborated = fields.Date(string='Fecha de Elaboración', required=True)
    date_approved = fields.Date(string='Fecha de Aprobación', required=True)

class MaintenanceService(models.Model):
    _name = 'materiales.service'

    program_id = fields.Many2one('materiales.programa', string='Programa de Mantenimiento')
    service_number = fields.Integer(string='No.')
    description = fields.Text(string='Descripción del Servicio', required=True)
    service_type = fields.Selection([('I', 'Interno'), ('E', 'Externo')], string='Tipo', required=True)
    maintenance_type = fields.Selection([('ENE', 'Enero'), ('FEB', 'Febrero'), ('MAR', 'Marzo'), ('ABR', 'Abril'), ('MAY', 'Mayo'), ('JUN', 'Junio'), ('JUL', 'Julio'), ('AGO', 'Agosto'), ('SEP', 'Septiembre'), ('OCT', 'Octubre'), ('NOV', 'Noviembre'), ('DIC', 'Diciembre')], string='Tiempo de Mantenimiento', required=True)
    schedule_date = fields.Date(string='Fecha de Programación')
    execution_date = fields.Date(string='Fecha de Ejecución')
    reschedule_cause = fields.Text(string='Causa de Reprogramación')
    reschedule_date = fields.Date(string='Fecha de Reprogramación')
