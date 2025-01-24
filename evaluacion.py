# -*- coding: utf-8 -*-

from openerp import models, fields

class Evaluacion(models.Model):
    _name = 'materiales.evaluacion'

    proveedor_id = fields.Many2one('materiales.proveedor', string='Proveedor a Evaluar', required=True)
    
    nombre_empresa = fields.Char(string='Nombre de la Empresa', related='proveedor_id.name', readonly=True)
    domicilio = fields.Char(string='Domicilio', related='proveedor_id.domicilio', readonly=True)
    correo = fields.Char(string='Correo', related='proveedor_id.correo', readonly=True)
    representante = fields.Char(string='Representante', related='proveedor_id.representante', readonly=True)
    ciudad = fields.Char(string='Ciudad', related='proveedor_id.ciudad', readonly=True)
    telefono = fields.Char(string='Telefono', related='proveedor_id.telefono', readonly=True)
    rfc = fields.Char(string='RFC', related='proveedor_id.rfc', readonly=True)
    
    # Campos para los criterios de evaluación
    criterio_1 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='1. Calidad de los procesos y servicios suministrados externamente.')

    criterio_2 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='2. Precio de los procesos y servicios suministrados externamente.')
    
    criterio_3 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='3. Cumplimiento del tiempo estimado para la ejecución de los procesos y servicios suministrados externamente')
    
    criterio_4 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='4. Ofrece garantía de los procesos y servicios suministrados externamente.')
    
    criterio_5 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='5. Respeta los reglamentos internos (no fumar, no ingerir bebidas alcohólicas o enervantes, no juegos de azar, entre otros).')
    
    criterio_6 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='6. No incurre en condiciones o actos inseguros, durante la ejecución de su servicio.')
    
    criterio_7 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='7. Los empleados cuentan con equipo de protección personal y lo utilizan.')
    
    criterio_8 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='8. Es responsable de los residuos generados, otorgando el manejo y la disposición final adecuada.')
    
    criterio_9 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='9. Respeta el medio ambiente, cuidando el uso y consumo de los recursos.')
    
    criterio_10 = fields.Selection([
        ('mala', 'Mala'), ('regular', 'Regular'), ('buena', 'Buena'), ('excelente', 'Excelente')
    ], string='10. Muestra respeto a los derechos humanos y la no discriminación.')
    
    evaluacion_obtenida= fields.Char(string='EVALUACIÓN OBTENIDA ', required=True)
    comentarios= fields.Text(string='COMENTARIOS ')