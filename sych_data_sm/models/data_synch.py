# -*- coding: utf-8 -*-

import xmlrpc.client
import ast
import logging
from pprint import pprint

from odoo import models, fields

_logger = logging.getLogger(__name__)


class SynchDataSM(models.Model):
    _name = "synch.data.sm"
    _description = 'Synch Data SM'

    url = fields.Char(string="URL")
    login = fields.Char(string="Login")
    pwd = fields.Char(string="Password")
    db_name = fields.Char(string="Database Name")

    def synch_product_presta_id(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [[]],
                                 {'fields': ['id', 'presta_id', 'condition', 'product_onsale', 'website_meta_title',
                                             'summary', 'website_meta_description', 'seo_name', 'website_published',
                                             'manufacturer_id', 'sp_eacute_specifications_techniques',
                                             'demande_catalogue']})
        for record in records:

            product_id = self.env['product.template'].search([
                ('id', '=', record['id'])

            ])
            if product_id:
                if record['presta_id']:
                    product_id.write({
                        'presta_id': record['presta_id'],
                    })
                if record['condition']:
                    product_id.write({
                        'condition': record['condition']
                    })
                if record['product_onsale']:
                    product_id.write({
                        'product_onsale': record['product_onsale']
                    })
                if record['website_meta_title']:
                    product_id.write({
                        'website_meta_title': record['website_meta_title']
                    })
                if record['summary']:
                    product_id.write({
                        'summary': record['summary']
                    })

                if record['website_meta_description']:
                    product_id.write({
                        'website_meta_description': record['website_meta_description']
                    })
                if record['seo_name']:
                    product_id.write({
                        'seo_name': record['seo_name']
                    })
                if record['website_published']:
                    product_id.write({
                        'website_published': record['website_published']
                    })

                if record['manufacturer_id']:
                    product_id.write({
                        'manufacturer_id': record['manufacturer_id'][0]
                    })
                if record['sp_eacute_specifications_techniques']:
                    product_id.write({
                        'sp_eacute_specifications_techniques': record['sp_eacute_specifications_techniques']
                    })
                if record['demande_catalogue']:
                    product_id.write({
                        'demande_catalogue': record['demande_catalogue']
                    })

    def synch_product_categories(self):

        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [[]],
                                 {'fields': ['id', 'presta_categ_id']})

        for record in records:
            if record['presta_categ_id']:
                pj_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                            'prestashop.category', 'search_read',
                                            [[
                                                ['id', '=', record['presta_categ_id'][0]],

                                            ]],
                                            {'fields': ['presta_id']})
                # print(pj_records)
                if pj_records:
                    categ_id = self.env['product.category'].search([
                        ('presta_id', '=', pj_records[0]['presta_id'])

                    ])
                    if categ_id:
                        product_id = self.env['product.template'].search([
                            ('id', '=', record['id'])

                        ])
                        if product_id:
                            product_id.categ_id = categ_id.id
            else:
                product_id = self.env['product.template'].search([
                    ('id', '=', record['id'])

                ])
                if product_id:
                    product_id.categ_id = False

    def synch_product_descrip(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [[]],
                                 {'fields': ['id', 'web_description']})
        for record in records:

            product_id = self.env['product.template'].search([
                ('id', '=', record['id'])

            ])
            if product_id:
                product_id.website_description = record['web_description']

    def synch_product_descrip_en(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        context_lang = {'lang': "en_US"}
        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [[['id', '=', 2670]]],
                                 {'fields': ['id', 'web_description'], 'context': context_lang})
        for record in records:

            product_id = self.env['product.template'].search([
                ('id', '=', record['id'])

            ])
            if product_id:
                product_id.with_context(lang="en_US").website_description = record['web_description']

    def synch_product_descrip_fr(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        context_lang = {'lang': "fr_FR"}
        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [[['id', '=', 2670]]],
                                 {'fields': ['id', 'web_description'], 'context': context_lang})
        for record in records:

            product_id = self.env['product.template'].search([
                ('id', '=', record['id'])

            ])
            if product_id:
                product_id.with_context(lang="fr_FR").website_description = record['web_description']

    def synch_product_categories_ids(self):
        # print('eee')
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [],
                                 {'fields': ['id', 'presta_categ_ids']})

        for record in records:
            new_categ = []
            if record['presta_categ_ids']:
                for categ_id in record['presta_categ_ids']:
                    pj_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                'prestashop.category', 'search_read',
                                                [[
                                                    ['id', '=', categ_id],

                                                ]],
                                                {'fields': ['presta_id']})
                    # # print(pj_records)
                    if pj_records:
                        categ16_id = self.env['product.category'].search([
                            ('presta_id', '=', pj_records[0]['presta_id'])

                        ])
                        if categ16_id:
                            new_categ.append(categ16_id.id)

            product_id = self.env['product.template'].search([
                ('id', '=', record['id'])

            ])
            if product_id:
                product_id.product_category_ids = new_categ

    def set_prestas_shop_onproduct(self):
        products_ids = self.env['product.template'].search([])

        if products_ids:
            for product in products_ids:
                product.tmpl_shop_ids = [1]

    def fix_empty_categ_presta(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'product.template', 'search_read',
                                 [[
                                     ['presta_categ_id', '=', False],
                                 ]],
                                 {'fields': ['id']})
        for record in records:
            product_id = self.env['product.template'].search([
                ('id', '=', record['id'])
            ])
            if product_id:
                product_id.write({'categ_id': False})

    def fix_manufacturer(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 'res.partner', 'search_read',
                                 [[
                                 ]],
                                 {'fields': ['id', 'presta_id', 'manufacturer']})
        for record in records:
            product_id = self.env['res.partner'].search([
                ('id', '=', record['id'])
            ])
            if product_id:
                if record['presta_id']:
                    product_id.write({'presta_id': record['presta_id']})

                product_id.write({'manufacturer': record['manufacturer']})
