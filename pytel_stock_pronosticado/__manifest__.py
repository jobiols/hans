# -*- coding: utf-8 -*-
{
    'name': "Pytel Stock Pronosticado Alertas",

    'summary': """
        Validaciones y alertas en base al stock pronosticado
        """,

    'description': """
    Validaciones y alertas en base al stock pronosticado
    
    
    """,

    'author': "HFOC",
    'website': "https://www.pytel.pe/",

    'category': 'stock',
    'version': '0.1',

    'depends': [
        'base',
        'stock', 
        'sale',
        'purchase',
    ],

    'data': [        
        'views/stock_alert.xml',
    ],
   
}