# -*- coding: utf-8 -*-
{
    'name': "custom_decor_theme",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Fawzi Boussentouh",


    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product', 'theme_decor', 'website_crm'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_decor_theme/static/src/js/hide_categ.js',
        ],
    },
    'pre_init_hook': 'disable_products_tab_bizople',
    # 'uninstall_hook': 'enable_products_tab_bizople',

}
