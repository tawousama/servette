# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

{
    'name': 'POS Customization',
    'version': '0.3',
    'category': 'POS',
    'summary': 'POS Customization',
    'description': """POS Customization""",

    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
    "depends": [
        'point_of_sale',
        'mass_mailing',

    ],
    'data': [
        'security/ir.model.access.csv',
        # 'views/templates.xml',
        'views/mailing_mailing_views.xml',
    ],
    'images': [
        'static/description/img.png'
    ],
    'qweb': [
        'static/src/xml/ClientDetailsEdit.xml',
        'static/src/xml/FieldMany2ManyTags.xml',
        'static/src/xml/OrderNote.xml',
        'static/src/xml/OrderReceipt.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {

        'point_of_sale.assets': [
            'pos_custom/static/src/css/pos.css',
            'pos_custom/static/src/js/models.js',
            # 'pos_custom/static/src/js/models_new.js',
            'pos_custom/static/src/js/FieldMany2ManyTags.js',
            'pos_custom/static/src/js/OrderWidget.js',
            'pos_custom/static/src/js/ClientDetailsEdit.js',
            'pos_custom/static/src/xml/ClientDetailsEdit.xml',
            'pos_custom/static/src/xml/FieldMany2ManyTags.xml',
            'web/static/lib/select2/select2.js',
            # 'pos_custom/static/src/js/select2.min.js',
        ],
    },
}
