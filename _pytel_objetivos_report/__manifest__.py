# -*- coding: utf-8 -*-
{
    'name': "Reporte de comisiones",

    'summary': """
                Reporte donde genera un excell  en el cual se visualizan la ganancia que le corresponde a cada empleado por su comision 
    """,

    'description': """
    
    """,
    'author': "Pytel",
    'version': '0.1',

    'depends': [
        'base',
        'product',
        '_pytel_objetivos_comision'
    ],

    'data': [
        'security/ir.model.access.csv', 
        'views/report.xml',
    ],
    'installable': True,
   
}