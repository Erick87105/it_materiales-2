# -*- coding: utf-8 -*-
from openerp import models, fields

class Criterios(models.Model):
    _name = 'materiales.criterios'   
    
    criterio_1 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='1. Calidad de los procesos y servicios suministrados externamente.', default=False, required=True)
    
    criterio_2 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='2. Precio de los procesos y servicios suministrados externamente.', default=False, required=True)
    
    criterio_3 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='3. Cumplimiento del tiempo estimado para la ejecución de los procesos y servicios suministrados externamente.', default=False, required=True)
    
    criterio_4 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='4. Ofrece garantía de los procesos y servicios suministrados externamente.', default=False, required=True)
    
    criterio_5 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='5. Respeta los reglamentos internos (no fumar, no ingerir bebidas alcohólicas o enervantes, no juegos de azar, entre otros).', default=False, required=True)
    
    criterio_6 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='6. No incurre en condiciones o actos inseguros, durante la ejecución de su servicio.', default=False, required=True)
    
    criterio_7 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='7. Los empleados cuentan con equipo de protección personal y lo utilizan.', default=False, required=True)
    
    criterio_8 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='8. Es responsable de los residuos generados, otorgando el manejo y la disposición final adecuada.', default=False, required=True)
    
    criterio_9 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='9. Respeta el medio ambiente, cuidando el uso y consumo de los recursos.', default=False, required=True)
    
    criterio_10 = fields.Selection([
        ('mala', 'Mala'),
        ('regular', 'Regular'),
        ('buena', 'Buena'),
        ('excelente', 'Excelente')
    ], string='10. Muestra respeto a los derechos humanos y la no discriminación.', default=False, required=True)
