# -*- coding: utf-8 -*-
{
    'name': "custom_decor_theme_2",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "FINOUTSOURCE",


    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product', 'theme_decor', 'website', 'website_sale'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        # 'views/views.xml',
        'data/ir_cron.xml',
        'data/out_of_stock_mail_template.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            ('before', 'theme_decor/static/src/scss/shop_products.scss',  'custom_decor_theme_2/static/src/scss/custom.scss'),
           
        ],
        'website.assets_wysiwyg': [
            'custom_decor_theme_2/static/src/xml/editor.xml',
        ]
        
    },
     'post_init_hook': 'post_init_hook',


}
