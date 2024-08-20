# -*- coding: utf-8 -*-

{
    'name': 'Rapport Etiquette SM',
    'author': 'Openfuture',
    'website': 'https://openfuture.ch/',
    'version': '14.0.0.1',
    'category': 'Inventory/Inventory',
    'description': """
    Rapport Etiquette SM
    """,
    'depends': [
        'stock',
    ],
    'data': [

        'report/report_lot_label_servette4.xml',
        'report/report_lot_label_servette3A4.xml',
        'report/report_lot_label_servette3.xml',
        'report/report_serial_barcode.xml',
        'report/template_report_servette_label.xml',

    ],

    'installable': True,
    'application': False,
}
