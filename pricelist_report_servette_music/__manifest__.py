# -*- coding: utf-8 -*-

{
    'name': 'Rapport Liste de prix Servette Music',
    'author': 'Openfuture',
    'website': 'https://openfuture.ch/',
    'version': '14.0.0.1',
    'category': 'Sales/Sales',
    'description': """
    Rapport Liste de prix Servette Music
    """,
    'depends': [
        'product',
    ],
    'data': [
        'views/product_template_views.xml',
        # 'views/product_templates.xml',
        'views/product_pricelist_views.xml',
        'report/product_pricelist_report_templates.xml',
        'report/product_report.xml',

    ],
    # 'qweb': ['static/src/xml/report_pricelist_search.xml'],

    'installable': True,
    'application': False,
    "assets": {
        "web.assets_backend": [
            "/pricelist_report_servette_music/static/src/js/product_pricelist_report.js",
            "pricelist_report_servette_music/static/src/xml/**/*",
        ],
    }
}
