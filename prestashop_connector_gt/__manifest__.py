# -*- coding: utf-8 -*-
##############################################################################
#    Globalteckz Pvt Ltd
##############################################################################

{
    "name": "Prestashop 1.7 Connector",
    "version": '16.0.1.0.0',
    "depends": ['base', 'contacts', 'stock', 'sale', 'delivery', 'account', 'product', 'sale_shop'],
    "author": "Globalteckz",
    'summary': 'Manage all your prestashop operations in Odoo Amazon Odoo Bridge(AOB) Amazon Odoo connector Odoo Amazon bridge Odoo amazon connector Connectors Odoo bridge Amazon to odoo Manage orders Manage products Import products Import customers Import orders Ebay to Odoo Odoo multi-channel bridge Multi channel connector Multi platform connector Multiple platforms bridge Connect Amazon with odoo Amazon bridge Flipkart Bridge Woocommerce odoo bridge Odoo woocommerce bridge Ebay odoo bridge  Odoo ebay bridge Multi channel bridge Prestashop odoo bridge Odoo prestahop Akeneo bridge Marketplace bridge Multi marketplace connector Multiple marketplace platform  odoo shopify shopify connector shopify bridge shipstation connector shipstation integration shipstation bridge odoo prestashop connector odoo presta shop connector odoo prestashop integration odoo prestashop 1.7 connector odoo prestashop 1.7 integration odoo prestashop bridge odoo presta shop bridge odoo prestashop bridge odoo prestashop 1.7 bridge odoo prestashop 1.7 bridge connector for prestashop website ecommerce module odoo app odoo 16 prestashop connection odoo prestashop plugins odoo prestashop website module connecteur odoo prestashop prestashop odoo connect multichannel prestashop odoo bridge prestashop 1.7 odoo bridge oca odoo prestashop odoo y prestashop' ,
    'images': ['static/description/Banner.gif'],
    "license": "Other proprietary",
    "price": "250.00",
    "currency": "USD",
    "description": """Prestashop E-commerce management""",
    "license": "Other proprietary",
    "website": "https://www.globalteckz.com/shop/odoo-apps/odoo-prestashop-connector/",
    'live_test_url' : 'https://www.youtube.com/watch?v=r9WkN0AtYhY',
    "category": "Ecommerce",
    "data": [
        'security/prestashop_security.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/schedular_data.xml',
        'data/sequence_data.xml',
        # 'data/custom_dashboard.xml',
        'wizard/create_shop_view.xml',
        'wizard/prestashop_connector_wizard_view.xml',
        'wizard/prestashop_import_export_operation_view.xml',
        # 'wizard/res_config_prestashop.xml',
        'wizard/prestashop_instance_configuration_wizard.xml',
        'views/prestashop_language_view.xml',
        'views/res_partner_view.xml',
        'views/res_partner_view.xml',
        'views/prestashop_view.xml',
        'views/stock_view.xml',
        'views/prestashop_onboarding_panel.xml',
        # 'views/instance_dashboard.xml',
        # 'views/prestashop_category_view.xml',
        'views/product_view.xml',
        'views/cart_rules.xml',
        'views/prestashop_logs_view.xml',
        # 'views/dashboard_menu.xml',
        'views/catalog_price_rule.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/order_message_view.xml',
        'views/dashboard_view.xml',
        'views/import_order_workflow.xml',
        'views/sale_shop.xml',
        'views/product_images_view.xml',
        'report/sale_report.xml',

        'views/prestashop_menus.xml',

    ],

    'qweb': [
        'static/src/xml/*.xml',
    ],
    'cloc_exclude': ['**/*.xml', ],
    'assets': {
        'web.assets_backend': [
            '/prestashop_connector_gt/static/src/css/graph_widget.scss',
            '/prestashop_connector_gt/static/src/scss/on_boarding_wizards.css',
            '/prestashop_connector_gt/static/src/scss/gt_graph_widget.scss',
            '/prestashop_connector_gt/static/src/js/prestashop_button.js',
            '/prestashop_connector_gt/static/src/js/graph_widget.js',
            # '/prestashop_connector_gt/static/src/js/prestashop_icon_view.js',
        ],
        'web.assets_qweb': [
            '/prestashop_connector_gt/static/src/xml/dashboard_widget.xml',
        ]
    },
    "active": True,
    "installable": True,
    'license': 'LGPL-3',
}
