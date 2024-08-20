# -*- coding: utf-8 -*-
# © 2020     Sinerkia iD (<https://www.sinerkia.com>).
{
    'name': 'Website Sale Hide Price and Add Cart',
    'version': '13.0.1.0.0',
    'category': 'Extra Tools',
'website': "https://softwareescarlata.com/",
    'sequence': 1,
    'summary': 'Website Sale Hide Price',
    'description': """
		Website Sale Hide Price
    """,
    'author': "David Montero Crespo",
    "depends": ['base','website_sale'],
    "data": [
        'views/template.xml',
        'views/product_template.xml',

    ],
    'images': ['static/description/logo.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 0,
    'currency': 'EUR',
    'license': 'AGPL-3',
}
