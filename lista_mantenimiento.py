# -- coding: iso-8859-15 --
from datetime import datetime

from openerp import api, models

class lista_mantenimiento(models.TransientModel):

    _name = 'report.it_materiales.solicitud_reporte_programa'

    @api.multi
    def render_html(self, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('it_materiales.solicitud_reporte_programa')

        docs = self.env[report.model].browse(self._ids)
        
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(self._ids),
        }
        
        return report_obj.render('it_materiales.solicitud_reporte_programa', docargs)