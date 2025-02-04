{
    'name': 'it_materiales',
    'version': '1.0',
    'category': 'Administración de Infraestructura y Servicios',
    'description': '"Módulo SIIT para el departamento de materiales del ITSA"',
    'author': 'EDUARDO MORENO MARTINEZ',
    'maintainer': 'I.S.C Javier Cisneros Lucatero ',
    'website': 'http://www.itsa.edu.mx',
    'depends': ['base', 'it_poa', 'it_base', 'report', 'document', 'mail'], # El módulo 'report' se usa para reportes en Odoo
    'data': [
        'views/vista_Reportes_Wizard.xml', 
        'views/parametros.xml',
        'views/ubicaciones.xml',
        'views/trabajadores.xml',
        'views/compras.xml',
        'views/recepcion.xml',
        'views/listaprecios.xml',
        'views/lista_verificacion.xml',
        'views/catalogoproductos.xml',
        'views/productos.xml',
        'views/entregaproductos.xml',
        'views/evaluacion.xml',
        'views/proveedor.xml',
        'views/criterios.xml',
        'views/categorias.xml',
        'views/departamentos.xml',
        'views/movimientos.xml',
        'views/ordentrabajo.xml',
        'views/solicitud_mantenimiento.xml',
        'views/programa_mantenimiento.xml',
        'reportes/solicitud_mante.xml', 
        'reportes/lista_compras.xml', 
        'reportes/programa_mantenimiento.xml',
        'reportes/evaluacion_proovedor.xml', 
        'reportes/compras_formato.xml', 
        'views/menu.xml'  
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}