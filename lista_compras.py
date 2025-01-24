# -- coding: iso-8859-15 --
from datetime import datetime

from openerp import api, models

class lista_compras(models.TransientModel):

# Con este metodo se pasan los datos del modelo al formato .xml donde se genera el diseño del reporte, es el vinculo en pocas palabras del modelo al .xml(template)
    _name = 'report.it_materiales.compras_reporte'

    @api.multi
    def render_html(self, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('it_materiales.compras_reporte')

        docs = self.env[report.model].browse(self._ids)
        
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(self._ids),
        }
        
        return report_obj.render('it_materiales.compras_reporte', docargs)