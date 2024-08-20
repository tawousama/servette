# -*- coding: utf-8 -*-

{
    'name': 'Servette Music - Partner',

    'author': 'Openfuture',

    'website': 'https://openfuture.ch/',

    'summary': 'Servette Music, partner',

    'version': '14.0.1.0',

    'category': 'Extra Tools',

    'description': """
   Servette Music Partner
    """,

    'depends': [
        'partner_firstname',

    ],
    'data': [
        #'views/res_partner_views.xml',

    ],
    'post_init_hook': 'post_init_hook',

    'installable': True,
    'application': False,
}
