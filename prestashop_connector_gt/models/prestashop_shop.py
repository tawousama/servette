# -*- coding: utf-8 -*-
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from datetime import timedelta, datetime, date, time
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.tools import float_compare
from bs4 import BeautifulSoup
import requests
import base64
import html

logger = logging.getLogger('__name__')

from odoo.addons.prestashop_connector_gt.prestapyt.prestapyt import PrestaShopWebService as PrestaShopWebService
from odoo.addons.prestashop_connector_gt.prestapyt.prestapyt import PrestaShopWebServiceDict as PrestaShopWebServiceDict
from odoo.addons.prestashop_connector_gt.prestapyt.prestapyt import \
    PrestaShopWebServiceImage as PrestaShopWebServiceImage

logger = logging.getLogger('stock')


class PrestashopShop(models.Model):
    _name = "prestashop.shop"
    _description = 'Prestashop Shop'

    code = fields.Char(string='Code')
    name = fields.Char('Name')

    prestashop_shop = fields.Boolean(string='Prestashop Shop')
    prestashop_instance_id = fields.Many2one('prestashop.instance', string='Prestashop Instance')
    presta_id = fields.Char(string='shop Id')

    ### Product Configuration
    product_import_condition = fields.Boolean(string="Create New Product if Product not in System while import order",
                                              default=True)
    route_ids = fields.Many2many('stock.route', 'shop_route_rel', 'shop_id', 'route_id', string='Routes')

    # Order Information
    company_id = fields.Many2one('res.company', string='Company', required=False,
                                 default=lambda s: s.env['res.company']._company_default_get('stock.warehouse'))
    prefix = fields.Char(string='Prefix')
    suffix = fields.Char(string='Suffix')
    shipment_fee_product_id = fields.Many2one('product.product', string="Shipment Fee",
                                              domain="[('type', '=', 'service')]")
    discount_product_id = fields.Many2one('product.product', string="Discount Fee", domain="[('type', '=', 'service')]")
    gift_wrapper_fee_product_id = fields.Many2one('product.product', string="Gift Wrapper Fee",
                                                  domain="[('type', '=', 'service')]")
    sale_journal = fields.Many2one('account.journal')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    partner_id = fields.Many2one('res.partner', string='Customer')
    workflow_id = fields.Many2one('import.order.workflow', string="Order Workflow")

    # stock Configuration
    on_fly_update_stock = fields.Boolean(string="Update on Shop at time of Odoo Inventory Change", default=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    # Schedular Configuration
    auto_import_order = fields.Boolean(string="Auto Import Order", default=True)
    auto_import_products = fields.Boolean(string="Auto Import Products", default=True)
    auto_update_inventory = fields.Boolean(string="Auto Update Inventory", default=True)
    auto_update_order_status = fields.Boolean(string="Auto Update Order Status", default=True)
    auto_update_product_data = fields.Boolean(string="Auto Update Product data", default=True)
    auto_update_price = fields.Boolean(string="Auto Update Price", default=True)

    # Import last date
    last_prestashop_inventory_import_date = fields.Datetime(string='Last Inventory Import Time')
    last_prestashop_product_import_date = fields.Datetime(string='Last Product Import Time')
    last_presta_product_attrs_import_date = fields.Datetime(string='Last Product Attributes Import Time')
    last_presta_cart_rule_import_date = fields.Datetime(string='Last Cart Rule Import Time')
    last_presta_catalog_rule_import_date = fields.Datetime(string='Last Catalog Rule Import Time')
    last_prestashop_order_import_date = fields.Datetime(string='Last Order Import Time')
    last_prestashop_carrier_import_date = fields.Datetime(string='Last Carrier Import Time')
    last_prestashop_msg_import_date = fields.Datetime(string='Last Message Import Time')
    last_prestashop_customer_import_date = fields.Datetime(string='Last Customer Import Time')
    last_prestashop_category_import_date = fields.Datetime(string='Last Category Import Time')
    last_prestashop_customer_address_import_date = fields.Datetime(string='Last Customer Address Import Time')
    last_attr_id = fields.Char("Attribute Id")

    last_product_feature_value_id_import = fields.Integer('Last Product Feature Value ID Import', default=0)
    last_product_feature_id_import = fields.Integer('Last Product Feature ID Import', default=0)

    # Update last date
    prestashop_last_update_category_date = fields.Datetime(string='Presta last update category date')
    prestashop_last_update_cart_rule_date = fields.Datetime(string='Presta last update cart rule date')
    prestashop_last_update_catalog_rule_date = fields.Datetime(string='Presta last update catalog rule date')
    prestashop_last_update_product_data_date = fields.Datetime(string='Presta last update product data rule date')
    prestashop_last_update_order_status_date = fields.Datetime(string='Presta last update order status date')

    # Export last date
    prestashop_last_export_product_data_date = fields.Datetime(string='Last Product Export Time')

    shop_physical_url = fields.Char(string="Physical URL", required=False, )
    last_product_attrs_id_import = fields.Integer('Last Product Attributes ID Import', default=0)
    last_product_attrs_values_id_import = fields.Integer('Last Product Attributes Values ID Import', default=0)
    last_product_category_id_import = fields.Integer('Last Product Category ID Import', default=0)
    last_product_id_import = fields.Integer('Last Product ID Import', default=0)
    last_order_id_id_import = fields.Integer('Last Order ID Import', default=0)
    last_message_id_import = fields.Integer('Last Message ID Import', default=0)
    last_catalog_rule_id_import = fields.Integer('Last Catalog Rule ID Import', default=0)
    last_cart_rule_id_import = fields.Integer('Last Cart Rule ID Import', default=0)
    last_product_inventory_import = fields.Integer('Last Product Inventory ID Import', default=0)
    last_delivery_carrier_import = fields.Integer('Last Product Inventory Import', default=0)
    last_customer_id_import = fields.Integer('Last Customer ID Import', default=0)
    last_supplier_id_import = fields.Integer('Last Supplier ID Import', default=0)
    last_manufacturers_id_import = fields.Integer('Last Manufacturers ID Import', default=0)
    last_address_id_import = fields.Integer('Last Address ID Import', default=0)
    last_country_id_import = fields.Integer('Last Country ID Import', default=0)
    last_state_id_import = fields.Integer('Last State ID Import', default=0)

    # import_prestashop_products_scheduler
    # @api.model
    def import_prestashop_products_scheduler(self, cron_mode=True):
        search_ids = self.search([('prestashop_shop', '=', True), ('auto_import_products', '=', True)])
        if search_ids:
            search_ids.sorted(reverse=True)
            search_ids.import_products()
        return True

    # update_prestashop_product_data_scheduler
    # @api.model
    def update_prestashop_product_data_scheduler(self, cron_mode=True):
        search_ids = self.search([('prestashop_shop', '=', True), ('auto_update_product_data', '=', True)])
        if search_ids:
            search_ids.sorted(reverse=True)
            search_ids.update_products()
        return True

    # update_prestashop_inventory_scheduler
    # @api.model
    def update_prestashop_inventory_scheduler(self, cron_mode=True):
        search_ids = self.search([('prestashop_shop', '=', True), ('auto_update_inventory', '=', True)])
        if search_ids:
            search_ids.sorted(reverse=True)
            search_ids.update_presta_product_inventory()
        return True

    # update_prestashop_order_status_scheduler
    # @api.model
    def update_prestashop_order_status_scheduler(self, cron_mode=True):
        search_ids = self.search([('prestashop_shop', '=', True), ('auto_update_order_status', '=', True)])
        if search_ids:
            search_ids.sorted(reverse=True)
            search_ids.update_order_status()
        return True

    def presta_connect(self):
        if self.prestashop_instance_id:
            presta_instance = self.prestashop_instance_id
        else:
            context = dict(self._context or {})
            active_id = context.get('active_ids')
            presta_instance = self.env['prestashop.instance'].browse(active_id)
        location = presta_instance.location
        webservicekey = presta_instance.webservice_key
        #         try:
        prestashop = PrestaShopWebService(location, webservicekey)
        #         except e:
        # PrestaShopWebServiceError
        #             print(str(e))
        return prestashop

    # @api.one
    def get_value_data(self, value):
        if isinstance(value, dict):
            return value.get('value')
        else:
            return value

    # @api.one
    def create_attribute(self, attribute, prestashop):
        attrs_id = False
        try:
            prod_att_obj = self.env['product.attribute']
            name = self.action_check_isinstance(attribute.get('name').get('language'))
            public_name = self.action_check_isinstance(attribute.get('public_name').get('language'))
            attribute_value = {
                'name': name[0].get('value'),
                'public_name': public_name[0].get('value'),
                'presta_id': attribute.get('id'),
                'display_type': attribute.get('group_type'),
                'is_presta': True
            }
            attrs_id = prod_att_obj.search([('presta_id', '=', attribute.get('id')), ('is_presta', '=', True)], limit=1)
            if not attrs_id:
                attrs_id = prod_att_obj.create(attribute_value)
            else:
                attrs_id.write(attribute_value)
            self.env.cr.execute(
                "select attr_id from attr_shop_rel where attr_id = %s and shop_id = %s" % (attrs_id.id, self.id))
            attr_data = self.env.cr.fetchone()
            if attr_data == None:
                self.env.cr.execute("insert into attr_shop_rel values(%s,%s)" % (attrs_id.id, self.id))
            self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': "New error", 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_attributes', 'error_lines': [(0, 0, {'log_description': 'atrs error'})]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return attrs_id

    def _create_attribute_values(self, attributes_vlaue, prestashop):
        attrs_value_id = False
        try:
            prod_att_obj = self.env['product.attribute']
            prod_attr_vals_obj = self.env['product.attribute.value']
            attribute_id = False
            if attributes_vlaue.get('id_attribute_group'):
                attribute_id = prod_att_obj.search(
                    [('presta_id', '=', attributes_vlaue.get('id_attribute_group')), ('is_presta', '=', True)], limit=1)
                if not attribute_id:
                    attribute_dict = prestashop.get('product_options', attributes_vlaue.get('id_attribute_group'))
                    attribute_id = self.create_attribute(attribute_dict.get('product_option'), prestashop)
            name = self.action_check_isinstance(attributes_vlaue.get('name').get('language'))
            attribute_value = {
                'name': name[0].get('value'),
                'presta_id': attributes_vlaue.get('id'),
                'attribute_id': attribute_id.id,
                'html_color': attributes_vlaue.get('color'),
                'is_presta': True
            }
            attrs_value_id = prod_attr_vals_obj.search(
                [('presta_id', '=', attributes_vlaue.get('id')), ('is_presta', '=', True)], limit=1)
            if not attrs_value_id:
                attrs_value_id = prod_attr_vals_obj.create(attribute_value)
            else:
                attrs_value_id.write(attribute_value)
            self.env.cr.execute("select attr_val_id from attr_val_shop_rel where attr_val_id = %s and shop_id = %s" % (
                attrs_value_id.id, self.id))
            attr_vals_data = self.env.cr.fetchone()
            if attr_vals_data == None:
                self.env.cr.execute("insert into attr_val_shop_rel values(%s,%s)" % (attrs_value_id.id, self.id))
            self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': "New error", 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_attributes', 'error_lines': [(0, 0, {'log_description': 'atrs error'})]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return attrs_value_id

    # @api.multi
    def import_product_attributes(self):
        for shop in self:
            try:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location, shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_product_attrs_id_import, 'limit': 1000}
                product_options = prestashop.get('product_options', options=filters)
                if product_options.get('product_options') and product_options.get('product_options').get(
                    'product_option'):
                    attributes = product_options.get('product_options').get('product_option')
                    if isinstance(attributes, list):
                        attributes = attributes
                    else:
                        attributes = [attributes]
                    for attribute in attributes:
                        shop.create_attribute(attribute, prestashop)
                        shop.write({'last_product_attrs_id_import': int(attribute.get('id'))})
                        self.env.cr.commit()

                value_filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_product_attrs_values_id_import,
                                 'limit': 2000}
                product_options_vals = prestashop.get('product_option_values', options=value_filters)
                if 'product_option_values' in product_options_vals and 'product_option_value' in product_options_vals.get(
                    'product_option_values'):
                    attributes_vlaues = product_options_vals.get('product_option_values').get('product_option_value')
                    if isinstance(attributes_vlaues, list):
                        attributes_vlaues = attributes_vlaues
                    else:
                        attributes_vlaues = [attributes_vlaues]
                    for attributes_vlaue in attributes_vlaues:
                        shop._create_attribute_values(attributes_vlaue, prestashop)
                        shop.write({'last_product_attrs_values_id_import': int(attributes_vlaue.get('id'))})
                        self.env.cr.commit()
            except Exception as e:
                raise ValidationError(_(str(e)))
        return True

    # @api.one

    def action_check_isinstance(self, data):
        if isinstance(data, list):
            data = data
        else:
            data = [data]
        return data

    def create_presta_category(self, category, prestashop):
        prod_category_obj = self.env['product.category']
        parent_id = categ_id = active = False
        try:
            if 'id_parent' in category and category.get('id_parent') != '0':
                parent_ids = prod_category_obj.search(
                    [('presta_id', '=', category.get('id_parent')), ('is_presta', '=', True)], limit=1)
                if parent_ids:
                    parent_id = parent_ids.id
                else:
                    parent_ids = prod_category_obj.search(
                        [('presta_id', '=', category.get('id_parent')), ('is_presta', '=', True),
                         ('active', '=', True)], limit=1)
                    if not parent_ids:
                        parent_id = parent_ids.id
            if category.get('active') == '1':
                active = True

            vals = {'presta_id': category.get('id'),
                    'parent_id': parent_id,
                    'is_presta': True,
                    'active': active,
                    'shop_ids': [(6, 0, [self.id])],
                    'meta_title': self.action_check_isinstance(category.get('meta_title').get('language'))[0].get(
                        'value'),
                    'meta_description': self.action_check_isinstance(category.get('meta_description').get('language'))[
                        0].get('value'),
                    'name': self.action_check_isinstance(category.get('name').get('language'))[0].get('value'),
                    }
            categ_id = prod_category_obj.create(vals)
            self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_categories', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return categ_id

    # @api.multi
    def import_categories(self):
        try:
            for shop in self:
                prod_category_obj = self.env['product.category']
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_product_category_id_import,
                           'limit': 500}
                presta_categ_data = prestashop.get('categories', options=filters)
                if presta_categ_data.get('categories') and presta_categ_data.get('categories').get('category'):
                    presta_categ = presta_categ_data.get('categories').get('category')
                    if isinstance(presta_categ, list):
                        presta_categ = presta_categ
                    else:
                        presta_categ = [presta_categ]
                    for category in presta_categ:
                        category_id = prod_category_obj.search(
                            [('presta_id', '=', category.get('id')), ('is_presta', '=', True)], limit=1)
                        if not category_id:
                            if category.get('id_parent') != '0':
                                parent_id = prod_category_obj.search(
                                    [('presta_id', '=', category.get('id_parent')), ('is_presta', '=', True)], limit=1)
                                if not parent_id:
                                    parent_id = prod_category_obj.search(
                                        [('presta_id', '=', category.get('id_parent')), ('is_presta', '=', True),
                                         ('active', '=', False)], limit=1)
                                    if not parent_id:
                                        try:
                                            parent_presta_categ_data = prestashop.get('categories',
                                                                                      category.get('id_parent'))
                                            shop.create_presta_category(parent_presta_categ_data.get('category'),
                                                                        prestashop)
                                            self.env.cr.commit()
                                        except Exception as e:
                                            logger.info('Parent category ===> %s' % (e))
                            shop.create_presta_category(category, prestashop)
                        shop.write({'last_product_category_id_import': int(category.get('id'))})
        except Exception as e:
            raise ValidationError(_(str(e)))
        return True

    def update_lang_presta_load_lang(self, id_lang, prestashop):
        lang_obj = self.env['res.lang']
        lang_id = False
        try:
            lang_data = prestashop.get('languages', id_lang)
            if lang_data and lang_data.get('language').get('iso_code'):
                lang_code = self.get_value_data(lang_data.get('language').get('iso_code'))
                if lang_code:
                    lang_id = lang_obj.search([('iso_code', '=', lang_code)])
                    if not lang_id:
                        lang_id = lang_obj.search([('iso_code', '=', lang_code), ('active', '=', False)])
                    if lang_id:
                        lang_id.write({'presta_id': id_lang, 'active': True})
                        self.env.cr.commit()
        except Exception as e:
            logger.info('Res Lang ===> %s' % (e))
        return lang_id

    # @api.one
    def create_customer(self, customer_detail, prestashop):
        res_partner_obj = self.env['res.partner']
        lang_obj = self.env['res.lang']
        cust_id = False
        dob = self.get_value_data(customer_detail.get('birthday'))

        date_obj = False
        try:
            if dob and dob != '0000-00-00':
                date_obj = datetime.strptime(dob, '%Y-%m-%d')
            lang_id = lang_obj.search([('presta_id', '=', customer_detail.get('id_lang'))])
            if not lang_id:
                lang_id = self.update_lang_presta_load_lang(customer_detail.get('id_lang'), prestashop)
            vals = {
                'presta_id': customer_detail.get('id'),
                'name': customer_detail.get('firstname') + ' ' + customer_detail.get('lastname') or ' ',
                'comment': customer_detail.get('note'),
                'lang': customer_detail.get('id_lang'),
                'customer_rank': 1,
                'supplier_rank': 0,
                'email': customer_detail.get('email'),
                'lang': lang_id.code,
                'website': customer_detail.get('website'),
                'prestashop_customer': True,
                'date_of_birth': date_obj and date_obj.date() or False,
            }

            if self.get_value_data(customer_detail.get('passwd')):
                customer_ids = res_partner_obj.search(
                    [('presta_id', '=', customer_detail.get('id')), ('prestashop_customer', '=', True)], limit=1)
                if not customer_ids:
                    cust_id = res_partner_obj.create(vals)
                    logger.info('Created Customer ===> %s' % (cust_id.id))
                else:
                    cust_id = customer_ids
                    customer_ids.write(vals)
                if cust_id:
                    self.env.cr.execute("select cust_id from customer_shop_rel where cust_id = %s and shop_id = %s" % (
                        cust_id.id, self.id))
                    cust_data = self.env.cr.fetchone()

                    if cust_data == None:
                        self.env.cr.execute("insert into customer_shop_rel values(%s,%s)" % (cust_id.id, self.id))
                self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_customers', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return cust_id

    # @api.multi
    def import_customers(self):
        for shop in self:
            res_partner_obj = self.env['res.partner']
            try:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)

                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_customer_id_import,
                           'filter[id_shop]': '%s' % self.presta_id, 'limit': 2000}
                customers_data = prestashop.get('customers', options=filters)
                if 'customers' in customers_data and 'customer' in customers_data.get('customers'):
                    customers = customers_data.get('customers').get('customer')
                    if isinstance(customers, list):
                        customers = customers
                    else:
                        customers = [customers]
                    for customer in customers:
                        customer_id = res_partner_obj.search(
                            [('presta_id', '=', customer.get('id')), ('prestashop_customer', '=', True)], limit=1)
                        if not customer_id:
                            self.create_customer(customer, prestashop)
                            self.write({'last_customer_id_import': int(customer.get('id'))})
                            self.env.cr.commit()
                self.env.cr.commit()
            except Exception as e:
                raise ValidationError(_(str(e)))
        return True

    # @api.one
    def create_presta_supplier(self, supplier):
        res_partner_obj = self.env['res.partner']
        try:
            vals = {
                'presta_id': supplier.get('id'),
                'name': supplier.get('name'),
                'supplier_rank': 0,
                'customer_rank': 0,
                'manufacturer': False,
                'prestashop_supplier': True,
            }
            logger.info('===vals======> %s', vals)

            supplier_id = res_partner_obj.search(
                [('presta_id', '=', supplier.get('id')), ('prestashop_supplier', '=', True)], limit=1)
            if not supplier_id:
                supplier_id = res_partner_obj.create(vals)
                logger.info('Created Supplier ===> %s' % (supplier_id.id))

            if supplier_id:
                self.env.cr.execute(
                    "select cust_id from customer_shop_rel where cust_id = %s and shop_id = %s" % (
                        supplier_id.id, self.id))
                supplier_data = self.env.cr.fetchone()

            if supplier_data == None:
                self.env.cr.execute("insert into customer_shop_rel values(%s,%s)" % (supplier_id.id, self.id))
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_suppliers', 'error_lines': [(0, 0, {'log_description': str(e)})]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return supplier_id

    # @api.multi
    def import_suppliers(self):
        for shop in self:
            try:
                res_partner_obj = self.env['res.partner']
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_supplier_id_import, 'limit': 2000}
                supplier_data = prestashop.get('suppliers', options=filters)
                if supplier_data.get('suppliers') and supplier_data.get('suppliers').get('supplier'):
                    suppliers = supplier_data.get('suppliers').get('supplier')
                    if isinstance(suppliers, list):
                        suppliers = suppliers
                    else:
                        suppliers = [suppliers]
                    for supplier in suppliers:
                        supplier_id = res_partner_obj.search(
                            [('presta_id', '=', supplier.get('id')), ('prestashop_supplier', '=', True)], limit=1)
                        if not supplier_id:
                            shop.create_presta_supplier(supplier)
            except Exception as e:
                raise ValidationError(_(str(e)))
        return True

    # @api.one
    def create_presta_manufacturers(self, manufacturer):
        res_partner_obj = self.env['res.partner']
        try:
            vals = {
                'presta_id': manufacturer.get('id'),
                'name': manufacturer.get('name'),
                'manufacturer': True,
                'customer_rank': 0,
                'supplier_rank': 0,
            }
            manufact_id = res_partner_obj.search(
                [('presta_id', '=', manufacturer.get('id')), ('manufacturer', '=', True)], limit=1)

            #### UPD
            loc = (self.prestashop_instance_id.location).split('//')
            url = "http://" + self.prestashop_instance_id.webservice_key + "@" + loc[
                1] + '/api/images/manufacturers/' + manufacturer.get('id')

            client = PrestaShopWebServiceImage(self.prestashop_instance_id.location,
                                               self.prestashop_instance_id.webservice_key)

            res = client.get_image(url)

            if res.get('image_content'):
                img_test = res.get('image_content').decode('utf-8')
                #extention = res.get('type')
                if img_test:
                    if manufact_id:
                        manufact_id.write({'image_1920': img_test})
                    else:
                        vals.update({'image_1920': img_test})
            ### END UPD

            if not manufact_id:
                manufact_id = res_partner_obj.create(vals)
                self.env.cr.commit()
                logger.info('Created manufacturer successfully ===> %s' % (manufact_id.id))

            if manufact_id:
                self.env.cr.execute("select cust_id from customer_shop_rel where cust_id = %s and shop_id = %s" % (
                    manufact_id.id, self.id))
                manufacturer_data = self.env.cr.fetchone()
            if manufacturer_data == None:
                self.env.cr.execute("insert into customer_shop_rel values(%s,%s)" % (manufact_id.id, self.id))
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_manufacturers', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return manufact_id

    # get manufacturers data from prestashop and create in odoo

    def import_manufacturers(self):
        for shop in self:
            try:
                res_partner_obj = self.env['res.partner']
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_manufacturers_id_import, 'limit': 2000}
                manufacturer_data = prestashop.get('manufacturers', options=filters)
                if manufacturer_data.get('manufacturers') and manufacturer_data.get('manufacturers').get(
                    'manufacturer'):
                    manufacturers = manufacturer_data.get('manufacturers').get('manufacturer')
                    if isinstance(manufacturers, list):
                        manufacturers = manufacturers
                    else:
                        manufacturers = [manufacturers]
                    for manufacturer in manufacturers:
                        manufacturer_id = res_partner_obj.search(
                            [('presta_id', '=', manufacturer.get('id')), ('manufacturer', '=', True)], limit=1)
                        if not manufacturer_id:
                            shop.create_presta_manufacturers(manufacturer)
                            self.write({'last_manufacturers_id_import': int(manufacturer.get('id'))})
                            self.env.cr.commit()
            except Exception as e:
                raise ValidationError(_(str(e)))
        return True

    def get_value(self, data):
        lang = self.env['prestashop.language'].search([])
        if isinstance(data, list):
            data = data
            lang_id = self.env['prestashop.language'].search(
                [('code', '=', 'it'), ('presta_instance_id', '=', self.prestashop_instance_id.id)])
            if not lang_id:
                lang = self.env['prestashop.language'].search([])
                lang_id = self.env['prestashop.language'].search(
                    [('code', '=', lang[0].code), ('presta_instance_id', '=', self.prestashop_instance_id.id)])[0]
        else:
            data = [data]
            lang_id = self.env['prestashop.language'].search([('presta_id', '=', data[0].get('attrs').get('id')), (
                'presta_instance_id', '=', self.prestashop_instance_id.id)])[0]
        val = [i for i in data if int(i.get('attrs').get('id')) == int(lang_id.presta_id)]
        return val[0]

    def import_country_state(self):
        browse_country_obj = self.env['res.country']
        browse_state_obj = self.env['res.country.state']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_country_id_import, 'limit': 100}
            state_filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_state_id_import, 'limit': 1000}
            prestashop_country_data = prestashop.get('countries', options=filters)
            print('\nprestashop_country_data+++++++++', prestashop_country_data)
            # import country
            if 'country' in prestashop_country_data.get('countries'):
                country_list = prestashop_country_data.get('countries').get('country')
                if isinstance(country_list, list):
                    country_list = country_list
                else:
                    country_list = [country_list]
                print("\ncountry_list+_+_+_+_+_+_+_+_+", country_list)
                for country in country_list:
                    country_vals = {'presta_id': country.get('id'), 'is_prestashop': True}
                    country_id = browse_country_obj.search([('code', '=', country.get('iso_code'))], limit=1)
                    if not country_id:
                        country_vals.update({'name': country.get('name').get('language')[0].get('value'),
                                             'code': country.get('iso_code')})

                        browse_country_obj.create(country_vals)
                    else:
                        country_id.write(country_vals)
                    shop.write({'last_country_id_import': int(country.get('id'))})
                    self.env.cr.commit()

            prestashop_state_data = prestashop.get('states', options=state_filters)
            if 'state' in prestashop_state_data.get('states'):
                state_list = prestashop_state_data.get('states').get('state')
                if isinstance(state_list, list):
                    state_list = state_list
                else:
                    state_list = [state_list]
                for state in state_list:
                    state_vals = {'presta_id': state.get('id'), 'is_prestashop': True}
                    country_id = browse_country_obj.search(
                        [('presta_id', '=', state.get('id_country')), ('is_prestashop', '=', True)], limit=1)

                    state_id = browse_state_obj.search([('name', '=', state.get('name'))], limit=1)
                    if state_id:
                        state_id.write(state_vals)
                    # if not state_id:
                    # 	state_vals.update({'name': state.get('name'), 'country_id': country_id.id,'code':state.get('iso_code')})
                    # 	browse_state_obj.create(state_vals)
                    # else:
                    # 	state_id.write(state_vals)
                    shop.write({'last_state_id_import': int(state.get('id'))})
                    self.env.cr.commit()
            # except Exception as e:
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'import_country_state',
            #              'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': False})
            #     self.env.context = new_context

    # def update_country_state_prestashop_id(self, id_country, id_state, prestashop):
    #     browse_country_obj = self.env['res.country']
    #     browse_state_obj = self.env['res.country.state']
    #     try:
    #         if isinstance(id_country, str):
    #             country_id = browse_country_obj.search([('presta_id', '=', id_country)], limit=1)
    #             if not country_id and id_state == False:
    #                 country_data = prestashop.get('countries', id_country)
    #                 country_name = self.get_value_data(
    #                     self.get_value(country_data.get('country').get('name').get('language')))
    #                 country_code = self.get_value_data(country_data.get('country').get('iso_code'))
    #                 country_id = browse_country_obj.create(
    #                     {'name': country_name, 'code': country_code, 'presta_id': id_country, 'is_prestashop': True})
    #                 self.env.cr.commit()
    #             return country_id
    #         if id_state:
    #             prestashop_state_data = prestashop.get('states', id_state)
    #             state_dict = prestashop_state_data.get('state')
    #             state_vals = {'presta_id': state_dict.get('id'), 'is_prestashop': True}
    #             state_id = browse_state_obj.search([('code', '=', state_dict.get('iso_code'))], limit=1)
    #             if not state_id:
    #                 state_vals.update({'name': state_dict.get('name'), 'country_id': id_country.id,
    #                                    'code': state_dict.get('iso_code')})
    #                 browse_state_obj.create(state_vals)
    #             else:
    #                 state_id.write(state_vals)
    #             return state_id
    #     except Exception as e:
    #         print('eee', str(e))

    def update_country_state_prestashop_id(self, id_country, id_state, prestashop):
        browse_country_obj = self.env['res.country']
        browse_state_obj = self.env['res.country.state']
        # print('id_country_+++++++++++++', id_country)
        try:
            if isinstance(id_country, str):
                country_data = prestashop.get('countries', id_country)
                # print("\ncountry_data_+++++++++++++++", country_data)
                country_code = country_data.get('country').get('iso_code')
                # print("country_code_++++++++++++", country_code)
                country_vals = {'presta_id': country_data.get('country').get('id'), 'is_prestashop': True}
                # print("country_vals_++++++++++++=", country_vals)
                country_id = browse_country_obj.search([('code', '=', country_code)], limit=1)
                # print("country_id+____________",country_id)
                # if not country_id and id_state == False:
                #     country_id.write(country_vals)
                return country_id
            if id_state:
                prestashop_state_data = prestashop.get('states', id_state)
                state_dict = prestashop_state_data.get('state')
                state_vals = {'presta_id': state_dict.get('id'), 'is_prestashop': True}
                state_id = browse_state_obj.search([('name', '=', state_dict.get('name'))], limit=1)
                if not state_id:
                    state_vals.update({'name': state_dict.get('name'), 'country_id': id_country.id,
                                       'code': state_dict.get('iso_code')})
                    browse_state_obj.create(state_vals)
                else:
                    state_id.write(state_vals)
                return state_id
        except Exception as e:
            log_id_obj = self.env['prestashop.log'].create(
                {'all_operations': 'import_addresses',
                 'error_lines': [
                     (
                         0, 0, {'log_description': str(e), })]})
            log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context

    def create_address(self, address_dict, prestashop):
        try:
            address_id = False
            res_partner_obj = self.env['res.partner']
            id_state = state_id = False
            country_id = self.update_country_state_prestashop_id(address_dict.get('id_country'), id_state, prestashop)
            if address_dict.get('id_state') != '0':
                state_id = self.update_country_state_prestashop_id(country_id, address_dict.get('id_state'), prestashop)
                if state_id:
                    state_id = state_id.id
            addr_vals = {
                'name': address_dict.get('firstname') + ' ' + address_dict.get('lastname'),
                'street': address_dict.get('address1'),
                'street2': address_dict.get('address2'),
                'city': address_dict.get('city'),
                'zip': address_dict.get('postcode'),
                'phone': address_dict.get('phone'),
                'mobile': address_dict.get('phone_mobile'),
                'address_id': address_dict.get('id'),
                'prestashop_address': True,
                'country_id': country_id.id,
                'state_id': state_id,
            }
            # print("addr_vals_++++++++++", addr_vals)
            parent_id = False
            if address_dict.get('id_customer') != '0':
                parent_id = res_partner_obj.search(
                    [('presta_id', '=', address_dict.get('id_customer')), ('prestashop_customer', '=', True)], limit=1)
                if not parent_id:
                    try:
                        cust_data = prestashop.get('customers', address_dict.get('id_customer'))
                        partner_id = self.create_customer(cust_data.get('customer'), prestashop)
                    except Exception as e:
                        logger.info('Error/Warning ' + str(e))
            elif address_dict.get('id_supplier') != '0':
                parent_id = res_partner_obj.search(
                    [('presta_id', '=', address_dict.get('id_supplier')), ('prestashop_supplier', '=', True)], limit=1)
                print('parent_id+_+parent_id_+_+_+', parent_id)
                if not parent_id:
                    try:
                        supplier_detail = prestashop.get('suppliers', address_dict.get('id_supplier'))
                        parent_id = self.create_presta_supplier(supplier_detail.get('supplier'))
                    except Exception as e:
                        logger.info('Error/Warning ' + str(e))
            elif address_dict.get('id_manufacturer') != '0':
                parent_id = res_partner_obj.search(
                    [('presta_id', '=', address_dict.get('id_manufacturer')), ('manufacturer', '=', True)], limit=1)
                if not parent_id:
                    try:
                        manufacturer_detail = prestashop.get('manufacturers', address_dict.get('id_manufacturer'))
                        parent_id = self.create_presta_manufacturers(manufacturer_detail.get('manufacturer'))
                    except Exception as e:
                        logger.info('Error/Warning ' + str(e))
            if parent_id:
                parent_id = parent_id.id
            addr_vals.update({'parent_id': parent_id})
            address_id = res_partner_obj.search(
                [('address_id', '=', address_dict.get('id')), ('prestashop_address', '=', True)])
            if address_id:
                address_id.write(addr_vals)
            else:
                address_id = res_partner_obj.create(addr_vals)
            self.env.cr.commit()
            return address_id
        except Exception as e:
            log_id_obj = self.env['prestashop.log'].create(
                {'all_operations': 'import_addresses',
                 'error_lines': [
                     (
                         0, 0, {'log_description': str(e), })]})
            log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context

    def import_addresses(self):
        res_partner_obj = self.env['res.partner']
        for shop in self:
            try:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_address_id_import, 'limit': 500}
                prestashop_address_data = prestashop.get('addresses', options=filters)
                if 'address' in prestashop_address_data.get('addresses'):
                    address_list = prestashop_address_data.get('addresses').get('address')
                    if isinstance(address_list, list):
                        address_list = address_list
                    else:
                        address_list = [address_list]
                    for address_dict in address_list:
                        address_id = res_partner_obj.search(
                            [('address_id', '=', address_dict.get('id')), ('prestashop_address', '=', True)])
                        if not address_id:
                            shop.create_address(address_dict, prestashop)
                            shop.write({'last_address_id_import': int(address_dict.get('id'))})
                        self.env.cr.commit()

            except Exception as e:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_addresses',
                     'error_lines': [
                         (
                             0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
                new_context = dict(self.env.context)
                new_context.update({'log_id': log_id})
                self.env.context = new_context
        return True

    def import_product_fetures(self):
        for shop in self:
            browse_product_feature_obj = self.env['product.feature']
            browse_product_feature_value_obj = self.env['product.feature.value']
            product_feature_options = {'product_features': ''}
            try:
                prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # filters = {'display': 'full', 'filter[id]': '>[%s]' % shop.last_product_feature_id_import,'limit': 1000}
                filters = {'display': 'full', 'limit': 1000}
                product_feature_options = prestashop.get('product_features', options=filters)
            except Exception as e:
                raise ValidationError(_(str(e)))
            if product_feature_options.get('product_features') and product_feature_options.get('product_features').get(
                'product_feature'):
                product_features = product_feature_options.get('product_features').get('product_feature')
                if isinstance(product_features, list):
                    product_features = product_features
                else:
                    product_features = [product_features]
                for product_feature in product_features:
                    custom_field_id = browse_product_feature_obj.search([('presta_id', '=', product_feature.get('id'))],
                                                                        limit=1)

                    name = self.get_value_data(product_feature.get('name').get('language'))
                    if not custom_field_id:
                        browse_product_feature_obj.create(
                            {'presta_id': product_feature.get('id'), 'position': product_feature.get('position'),
                             'name': name})
                    shop.write({'last_product_feature_id_import': int(product_feature.get('id'))})
                    self.env.cr.commit()

            # value_filters = {'display': 'full', 'filter[id]': '>[%s]' % shop.last_product_feature_value_id_import,
            #                  'limit': 5000}
            value_filters = {'display': 'full', 'limit': 5000}
            product_feature_values_option = prestashop.get('product_feature_values', options=value_filters)
            if 'product_feature_values' in product_feature_values_option and 'product_feature_value' in product_feature_values_option.get(
                'product_feature_values'):
                product_features_vlaues = product_feature_values_option.get('product_feature_values').get(
                    'product_feature_value')

                if isinstance(product_features_vlaues, list):
                    product_features_vlaues = product_features_vlaues
                else:
                    product_features_vlaues = [product_features_vlaues]
                for product_features_vlaue in product_features_vlaues:
                    custom_field_value_id = browse_product_feature_value_obj.search(
                        [('presta_id', '=', product_features_vlaue.get('id'))], limit=1)
                    name = self.get_value_data(product_features_vlaue.get('value').get('language'))
                    if not custom_field_value_id:
                        feature_value = browse_product_feature_obj.search(
                            [('presta_id', '=', product_features_vlaue.get('id_feature'))], limit=1)
                        browse_product_feature_value_obj.create(
                            {'presta_id': product_features_vlaue.get('id'),
                             'feature_id': feature_value.id, 'name': name})
                    shop.write({'last_product_feature_value_id_import': int(product_features_vlaue.get('id'))})
                    self.env.cr.commit()
            if product_feature_options.get('product_features') == '' and product_feature_values_option.get(
                'product_feature_values') == '':
                raise ValidationError(_('Successfully Imported feature'))
        return True

    # @api.one
    def create_presta_product(self, product_dict, prestashop):
        prod_temp_obj = self.env['product.template']
        prod_prod_obj = self.env['product.product']
        att_val_obj = self.env['product.attribute.value']
        product_image_obj = self.env['gt.prestashop.product.images']
        res_partner_obj = self.env['res.partner']
        product_categ_obj = self.env['product.category']
        account_tax_group_obj = self.env['account.tax.group']
        product_supplier_info_obj = self.env['product.supplierinfo']
        try:
            manufacturers_id = supplier_id = False
            if self.action_check_isinstance(product_dict.get('name').get('language'))[0].get('value'):
                prd_tmp_vals = {
                    'name': self.action_check_isinstance(product_dict.get('name').get('language'))[0].get('value'),
                    'detailed_type': 'product',
                    'list_price': product_dict.get('price'),
                    'default_code': product_dict.get('reference'),
                    'prestashop_product': True,
                    'taxes_id': False,
                    'wholesale_price': product_dict.get('wholesale_price'),
                    'website_description':
                        self.action_check_isinstance(product_dict.get('description').get('language'))[
                            0].get('value'),
                    'standard_price': product_dict.get('wholesale_price'),
                    'product_onsale': product_dict.get('on_sale'),
                    'on_sale': product_dict.get('on_sale'),
                    # 'product_instock': self.get_value(product_dict.get('available_now').get('language')),
                    'product_lngth': product_dict.get('depth'),
                    'product_width': product_dict.get('width'),
                    'product_wght': product_dict.get('weight'),
                    'product_hght': product_dict.get('height'),
                    'presta_id': product_dict.get('id'),

                }
                print("prd_tmp_vals__+_++_+_+_+_", prd_tmp_vals)
                if product_dict.get('id_tax_rules_group') not in ['0', '']:
                    tax_group_id = account_tax_group_obj.search(
                        [('presta_id', '=', product_dict.get('id_tax_rules_group'))], limit=1)
                    prd_tmp_vals.update({'tax_group_id': tax_group_id.id})

                if product_dict.get('id_category_default'):
                    domain_categ = [('presta_id', '=', product_dict.get('id_category_default')),
                                    ('is_presta', '=', True),
                                    ('active', '=', True)]
                    cate_id = self.search_record_in_odoo(product_categ_obj, domain_categ)
                    if cate_id:
                        prd_tmp_vals.update({'categ_id': cate_id.id})
                if product_dict.get('ean13') not in ['0', '']:
                    check_product = False
                    if self.prestashop_instance_id.mapped_product_by == 'default_code' or self.prestashop_instance_id.mapped_product_by == 'presta_id':
                        check_product = prod_prod_obj.search([('barcode', '=', product_dict.get('ean13'))], limit=1)
                    if not check_product:
                        prd_tmp_vals.update({'barcode': product_dict.get('ean13')})
                    else:
                        log_id_obj = self.env['prestashop.log'].create(
                            {'log_name': 'Barcode : ' + str(product_dict.get('ean13')) + 'Already present',
                             'all_operations': 'import_products', 'error_lines': [(0, 0, {
                                'log_description': 'existing in Odoo Internal ref: ' + str(
                                    check_product.default_code)}), (
                                                                                      0, 0, {
                                                                                          'log_description': ' New trying create product Internal ref: ' + str(
                                                                                              check_product.default_code)})]})
                # get manufacturer id if not in odoo create
                if product_dict.get('id_manufacturer') != '0':
                    manufacturers_id = res_partner_obj.search(
                        [('presta_id', '=', product_dict.get('id_manufacturer')), ('manufacturer', '=', True)], limit=1)
                    if not manufacturers_id:
                        try:
                            manufacturer_detail = prestashop.get('manufacturers', product_dict.get('id_manufacturer'))
                            manufact_id = self.create_presta_manufacturers(manufacturer_detail.get('manufacturer'))
                            if manufact_id:
                                manufacturers_id = manufact_id.id
                        except Exception as e:
                            manufacturers_id = False
                    else:
                        manufacturers_id = manufacturers_id.id
                prd_tmp_vals.update({'manufacturer_id': manufacturers_id})

                # get supplier id if not in odoo create
                if product_dict.get('id_supplier') != '0':
                    supplier_id = res_partner_obj.search(
                        [('presta_id', '=', product_dict.get('id_supplier')), ('prestashop_supplier', '=', True)],
                        limit=1)
                    if supplier_id:
                        supplier_id = supplier_id.id
                    else:
                        try:
                            supplier_detail = prestashop.get('suppliers', product_dict.get('id_supplier'))
                            supply_id = self.create_presta_supplier(supplier_detail.get('supplier'))
                            if supply_id:
                                supplier_id = supply_id.id
                        except Exception as e:
                            supplier_id = False
                # if supplier_id:
                # 	prd_tmp_vals.update({'supplier_id': supplier_id})
                # 	prd_tmp_vals.update({'seller_ids': [(0, 0, {'name': supplier_id})]})
                if product_dict.get('associations'):
                    attribute_line_ids, atttibute_lines_dict = [], {}
                    if product_dict.get('associations').get('product_option_values'):
                        if product_dict.get('associations').get('product_option_values').get('product_option_value'):
                            data = product_dict.get('associations').get('product_option_values').get(
                                'product_option_value')
                        else:
                            data = product_dict.get('associations').get('product_option_values')
                        if data:
                            if isinstance(data, dict):
                                data = [data]
                            for att_val in data:
                                if att_val.get('value') in ('', '0'):
                                    continue
                                value_id = att_val_obj.search(
                                    [('presta_id', '=', self.get_value_data(att_val.get('id')))],
                                    limit=1)
                                if not value_id:
                                    try:
                                        values_data = prestashop.get('product_option_values',
                                                                     self.get_value_data(att_val.get('id')))
                                        self._create_attribute_values(values_data.get('product_option_value'),
                                                                      prestashop)
                                        self.env.cr.commit()
                                    except Exception as e:
                                        value_id = False
                                    value_id = att_val_obj.search(
                                        [('presta_id', '=', self.get_value_data(att_val.get('id')))], limit=1)
                                if value_id:
                                    if value_id.attribute_id.id in atttibute_lines_dict:
                                        if value_id.id not in atttibute_lines_dict.get(value_id.attribute_id.id):
                                            atttibute_lines_dict.get(value_id.attribute_id.id).append(value_id.id)
                                    else:

                                        atttibute_lines_dict.update({value_id.attribute_id.id: [value_id.id]})
                            for i in atttibute_lines_dict.keys():
                                attribute_line_ids.append(
                                    (0, 0, {'attribute_id': i, 'value_ids': [(6, 0, atttibute_lines_dict.get(i))]}))
                            prd_tmp_vals.update({'attribute_line_ids': attribute_line_ids})
                product_domain = []
                if self.prestashop_instance_id.mapped_product_by == 'default_code':
                    product_domain.append(('default_code', '=', prd_tmp_vals.get('default_code')))
                elif self.prestashop_instance_id.mapped_product_by == 'barcode':
                    product_domain.append(('barcode', '=', prd_tmp_vals.get('barcode')))
                else:
                    product_domain.append(('presta_id', '=', self.get_value_data(product_dict.get('id'))))
                prod_id = prod_temp_obj.search(product_domain, limit=1)
                if not prod_id:
                    print('++++++++++++++creating product template+++++++++++++++++')
                    prod_id = prod_temp_obj.create(prd_tmp_vals)
                else:
                    if prd_tmp_vals.get('attribute_line_ids'):
                        prd_tmp_vals.pop('attribute_line_ids')
                    print('++++++++++++++writing product template+++++++++++++++++')
                    prod_id.write(prd_tmp_vals)
                    prd_tmp_vals.update({'attribute_line_ids': attribute_line_ids})
                self.env.cr.commit()
                print('\n\nprod_id++++++++++++++++++', prod_id)
                if prod_id:
                    if supplier_id:
                        print("supplier_id+_+_+_+_+_+_+_", supplier_id)
                        temp_supplier = product_supplier_info_obj.search(
                            [('product_tmpl_id', '=', prod_id.id), ('partner_id', '=', supplier_id)])
                        if not temp_supplier:
                            product_supplier_info_obj.create({'partner_id': supplier_id, 'product_tmpl_id': prod_id.id})
                    # Image create/write
                    img_ids = product_dict.get('associations').get('images').get('image', False)
                    if img_ids:
                        if isinstance(img_ids, list):
                            img_ids = img_ids
                        else:
                            img_ids = [img_ids]
                        for image in img_ids:
                            if image.get('id') != '0':
                                loc = (self.prestashop_instance_id.location).split('//')
                                url = "http://" + self.prestashop_instance_id.webservice_key + "@" + loc[
                                    1] + '/api/images/products/' + product_dict.get('id') + '/' + image.get('id')
                                client = PrestaShopWebServiceImage(self.prestashop_instance_id.location,
                                                                   self.prestashop_instance_id.webservice_key)
                                res = client.get_image(url)
                                if res.get('image_content'):
                                    img_test = res.get('image_content').decode('utf-8')
                                    extention = res.get('type')
                                    if img_test:
                                        product_img_id = product_image_obj.search(
                                            [('prest_img_id', '=', int(image.get('id'))),
                                             ('product_t_id', '=', prod_id.id)])
                                        if not product_img_id:
                                            is_default_img = False
                                            if product_dict.get('id_default_image').get('value') is not None:
                                                is_default_img = True
                                                prod_id.write({'image_1920': img_test})
                                            img_vals = (
                                                {'is_default_img': is_default_img, 'extention': extention,
                                                 'image_url': url,
                                                 'image': img_test, 'prest_img_id': int(image.get('id')), 'name': ' ',
                                                 'product_t_id': prod_id.id})
                                            product_image_obj.create(img_vals)
                    # 	# write attributes
                    if prd_tmp_vals.get('attribute_line_ids'):
                        for each in prd_tmp_vals.get('attribute_line_ids'):
                            attribute_ids = self.env['product.template.attribute.line'].search(
                                [('product_tmpl_id', '=', prod_id.id),
                                 ('attribute_id', '=', each[2].get('attribute_id'))])
                            if attribute_ids:
                                for val_at in each[2].get('value_ids')[0][2]:
                                    if val_at not in attribute_ids[0].value_ids.ids:
                                        attribute_ids[0].write({'value_ids': [(6, 0, [val_at])]})
                            else:
                                self.env['product.template.attribute.line'].create(
                                    {'attribute_id': each[2].get('attribute_id'), 'product_tmpl_id': prod_id.id,
                                     'value_ids': each[2].get('value_ids')})
                        if prd_tmp_vals.get('attribute_line_ids'):
                            prd_tmp_vals.pop('attribute_line_ids')
                    prod_id.write(prd_tmp_vals)
                    self.env.cr.execute(
                        "select product_id from product_templ_shop_rel_ where product_id = %s and shop_id = %s" % (
                            prod_id.id, self.id))
                    prod_data = self.env.cr.fetchone()
                    if prod_data == None:
                        self.env.cr.execute("insert into product_templ_shop_rel_ values(%s,%s)" % (prod_id.id, self.id))
                    logger.info('Producrt Created ===> %s', prod_id.id)
                    self.env.cr.execute(
                        "select product_id from product_templ_shop_rel_ where product_id = %s and shop_id = %s" % (
                            prod_id.id, self.id))
                    prod_data = self.env.cr.fetchone()
                    if prod_data == None:
                        q1 = "insert into product_templ_shop_rel_ values(%s,%s)" % (prod_id.id, self.id)
                        self.env.cr.execute(q1)

                    if product_dict.get('associations').get('combinations').get('combination', False):
                        comb_l = product_dict.get('associations').get('combinations').get('combination', False)
                        c_val = {}
                        if comb_l:
                            if isinstance(comb_l, list):
                                comb_l = comb_l
                            else:
                                comb_l = [comb_l]

                            # main code for get product product from product template importing prestashop product
                            for comb in comb_l:
                                try:
                                    combination_dict = prestashop.get('combinations',
                                                                      self.get_value_data(comb.get('id')))
                                    value_list = []
                                    value_comb_ids = combination_dict.get('combination').get('associations').get(
                                        'product_option_values').get('product_option_value')
                                    if value_comb_ids:
                                        if isinstance(value_comb_ids, list):
                                            value_comb_ids = value_comb_ids
                                        else:
                                            value_comb_ids = [value_comb_ids]
                                        for each in value_comb_ids:
                                            val_id = self.get_value_data(each.get('id'))
                                            value_list.append(val_id)
                                        prest_product_id = self.get_value_data(
                                            combination_dict.get('combination').get('id_product'))
                                        product_ids = prod_prod_obj.search(
                                            [('product_tmpl_id.presta_id', '=', prest_product_id)])
                                        prod_id_var = False
                                        line_list = []
                                        if product_ids:
                                            for product_data in product_ids:
                                                prod_val_ids = product_data.product_template_attribute_value_ids.product_attribute_value_id
                                                k = []
                                                for red in prod_val_ids:
                                                    k.append(red.presta_id)
                                                res = k
                                                rles = sorted(res, key=int)
                                                t = self.get_value_data(value_list)
                                                imag_odoo_data = False
                                                if rles == t:
                                                    img_ids = combination_dict.get('combination').get(
                                                        'associations').get(
                                                        'images').get('image', False)
                                                    if img_ids:
                                                        if isinstance(img_ids, list):
                                                            img_ids = img_ids
                                                        else:
                                                            img_ids = [img_ids]
                                                        for image in img_ids:
                                                            if image.get('id') != '0':
                                                                imag_odoo_data = self.return_image_data(prestashop,
                                                                                                        product_data.product_tmpl_id.id,
                                                                                                        prest_product_id,
                                                                                                        image.get('id'))
                                                    product_barcode = False
                                                    if self.get_value_data(
                                                        combination_dict.get('combination').get('ean13')) not in [
                                                        '',
                                                        '0']:
                                                        product_barcode = self.get_value_data(
                                                            combination_dict.get('combination').get('ean13'))

                                                    # product code
                                                    print('\nc_val+++++++++++++', c_val)
                                                    print('\ncombination_dict++++++++++++', combination_dict)

                                                    c_val.update({
                                                        'default_code': self.get_value_data(
                                                            combination_dict.get('combination').get('reference')),
                                                        'barcode': product_barcode,
                                                        'weight': self.get_value_data(
                                                            combination_dict.get('combination').get('weight')),
                                                        'combination_id': self.get_value_data(
                                                            combination_dict.get('combination').get('id')),
                                                        'standard_price': self.get_value_data(
                                                            combination_dict.get('combination').get('wholesale_price')),
                                                    })

                                                    if imag_odoo_data:
                                                        c_val.update({
                                                            'image_1920': imag_odoo_data.image
                                                        })
                                                        print("c_val+_+_+_+_+__+_+", c_val)
                                                    product_data.product_template_attribute_value_ids.write({
                                                        'price_extra': self.get_value_data(
                                                            combination_dict.get('combination').get('price'))})
                                                    print('last------------->>>>>>>>>>>>>>>')

                                                    product_data.write(c_val)
                                                    print("product_data+_+_+_+_+_", product_data)
                                except Exception as e:
                                    continue
                        self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_products', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return True

    def return_image_data(self, product_id, product_presta_id, img_id):
        product_image_obj = self.env['gt.prestashop.product.images']
        product_img_id = product_image_obj.search(
            [('prest_img_id', '=', int(img_id)), ('product_t_id', '=', product_id)])
        if not product_img_id:
            try:
                loc = (self.prestashop_instance_id.location).split('//')
                url = "http://" + self.prestashop_instance_id.webservice_key + "@" + loc[
                    1] + '/api/images/products/' + product_presta_id + '/' + img_id
                client = PrestaShopWebServiceImage(self.prestashop_instance_id.location,
                                                   self.prestashop_instance_id.webservice_key)
                res = client.get_image(url)
                if res.get('image_content'):
                    img_test = res.get('image_content').decode('utf-8')
                    extention = res.get('type')
                    if img_test:
                        product_img_id = product_image_obj.search(
                            [('prest_img_id', '=', int(img_id)), ('product_t_id', '=', product_id)])
                        if not product_img_id:
                            img_vals = ({'is_default_img': False,
                                         'extention': extention, 'image_url': url,
                                         'image': img_test,
                                         'prest_img_id': int(img_id),
                                         'name': 'test',
                                         'product_t_id': product_id})
                            product_image_obj.create(img_vals)
            except Exception as e:
                product_img_id = False

        return product_img_id

    def search_record_in_odoo(self, brows_obj, domain):
        record_id = brows_obj.search(domain)
        if not record_id:
            domain.append(('active', '=', False))
            record_id = brows_obj.search(domain)
        return record_id

    def import_products(self):
        for shop in self:
            # try:
            product_categ_obj = self.env['product.category']
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_product_id_import, 'limit': [0, 200]}
            prestashop_product_data = prestashop.get('products', options=filters)
            if prestashop_product_data.get('products') and prestashop_product_data.get('products').get('product'):
                prestashop_product_list = prestashop_product_data.get('products').get('product')
                prestashop_product_list = self.action_check_isinstance(prestashop_product_list)
                for product_dict in prestashop_product_list:
                    if product_dict.get('id_category_default'):
                        domain_categ = [('presta_id', '=', product_dict.get('id_category_default')),
                                        ('is_presta', '=', True)]
                        cate_id = self.search_record_in_odoo(product_categ_obj, domain_categ)
                        if not cate_id:
                            try:
                                parent_presta_categ_data = prestashop.get('categories',
                                                                          product_dict.get('id_category_default'))
                                shop.create_presta_category(parent_presta_categ_data.get('category'), prestashop)
                                self.env.cr.commit()
                            except Exception as e:
                                logger.info('Parent category ===> %s' % (e))
                    shop.create_presta_product(product_dict, prestashop)
                    shop.write({'last_product_id_import': product_dict.get('id')})
                    self.env.cr.commit()
        #     except Exception as e:
        #         if self.env.context.get('log_id'):
        #             log_id = self.env.context.get('log_id')
        #             self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
        #         else:
        #             log_id_obj = self.env['prestashop.log'].create(
        #                 {'all_operations': 'import_products', 'error_lines': [(0, 0, {'log_description': str(e), })]})
        #             log_id = log_id_obj.id
        #         new_context = dict(self.env.context)
        #         new_context.update({'log_id': log_id})
        #         self.env.context = new_context
        # return True

    def createInventory(self, stock, lot_stock_id, prestashop):
        product_obj = self.env['product.product']
        product_temp_obj = self.env['product.template']
        quantity = int(stock.get('quantity'))
        product_id = False
        try:
            if stock.get('id_product_attribute') != '0':
                product_id = product_obj.search([('combination_id', '=', stock.get('id_product_attribute'))], limit=1)
            if not product_id:
                product_id = product_obj.search([('product_tmpl_id.presta_id', '=', stock.get('id_product'))], limit=1)
            if product_id:
                self.env.cr.execute(
                    "select product_prod_id from product_prod_shop_rel where product_prod_id = %s and shop_id = %s" % (
                        product_id.id, self.id))
                prod_data = self.env.cr.fetchone()
                if prod_data is None:
                    self.env.cr.execute("insert into product_prod_shop_rel values(%s,%s)" % (product_id.id, self.id))
                date = datetime.now()
                self.env['stock.quant'].create({
                    'location_id': lot_stock_id,
                    'product_id': product_id.id,
                    'inventory_quantity': quantity,
                    'inventory_date': date,
                    'presta_id': stock.get('id'),
                    'is_presta': True
                }).action_apply_inventory()
                self.env.cr.commit()
                return True
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_inventory', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context

    # @api.multi
    def import_product_inventory(self):
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_product_inventory_import,
                       'filter[id_shop]': '%s' % self.presta_id, 'limit': 5000}
            prestashop_stock_data = prestashop.get('stock_availables', options=filters)
            if prestashop_stock_data and 'stock_availables' in prestashop_stock_data and 'stock_available' in prestashop_stock_data.get(
                'stock_availables'):
                stocks = prestashop_stock_data.get('stock_availables').get('stock_available')
                if isinstance(stocks, list):
                    stocks = stocks
                else:
                    stocks = [stocks]
                for stock in stocks:
                    stock_id = self.env['stock.quant'].search(
                        [('presta_id', '=', stock.get('id')), ('is_presta', '=', True)])
                    if not stock_id:
                        shop.createInventory(stock, shop.warehouse_id.lot_stock_id.id, prestashop)
                    shop.write({'last_product_inventory_import': stock.get('id')})
        # except Exception as e:
        # 	raise ValidationError(_(str(e)))
        return True

    # @api.one
    def create_carrier(self, carrier_dict):
        carrier_obj = self.env['delivery.carrier']
        product_obj = self.env['product.product']
        car_id = False
        try:
            product_id = product_obj.search([('name', '=', carrier_dict.get('name'))], limit=1)
            if not product_id:
                product_id = product_obj.create({'name': carrier_dict.get('name')})
            carr_vals = {
                'name': carrier_dict.get('name'),
                'fixed_price': int(carrier_dict.get('shipping_external')),
                'product_id': product_id.id,
                'is_presta': True,
                'delay_comment': True,
                'presta_id': carrier_dict.get('id'),
                'delay_comment': self.get_value_data(self.get_value(carrier_dict.get('delay').get('language')))
            }
            car_id = carrier_obj.search([('presta_id', '=', carrier_dict.get('id')), ('is_presta', '=', True)], limit=1)
            if not car_id:
                car_id = carrier_obj.create(carr_vals)
                logger.info('created carrier ===> %s', car_id.id)
            self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_carriers', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context

        return car_id

    # @api.multi
    def import_carriers(self):
        for shop in self:
            # try:
            carrier_obj = self.env['delivery.carrier']
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            filters = {'display': 'full', 'filter[id]': '>[%s]' % self.last_delivery_carrier_import, 'limit': 100}
            prestashop_carriers_data = prestashop.get('carriers', options=filters)
            if prestashop_carriers_data.get('carriers') and prestashop_carriers_data.get('carriers').get('carrier'):
                carriers = prestashop_carriers_data.get('carriers').get('carrier')
                if isinstance(carriers, list):
                    carriers = carriers
                else:
                    carriers = [carriers]
                for carrier in carriers:
                    carrier_id = carrier_obj.search(
                        [('presta_id', '=', carrier.get('id')), ('is_presta', '=', True)], limit=1)
                    if not carrier_id:
                        shop.create_carrier(carrier)
                    shop.write({'last_delivery_carrier_import': carrier.get('id')})
            return True
            # except Exception as e:
            #     raise ValidationError(_(str(e)))

    # workflow of order
    # def manageOrderWorkflow(self, saleorderid, order_detail, status):
    #
    #     print('\nsaleorderid+++++++++++++', saleorderid)
    #     print('\norder_detail+++++++++++++', order_detail)
    #     print('\nstatus+++++++++++++', status)
    #
    #     invoice_obj = self.env['account.move']
    #     return_obj = self.env['stock.return.picking']
    #     return_line_obj = self.env['stock.return.picking.line']
    #
    #     if saleorderid:
    #         if status.name == 'Canceled':
    #             eroorrrg
    #             if saleorderid.state in ['draft']:
    #                 saleorderid.action_cancel()
    #         if status.name == 'Awaiting check payment':
    #             erorrrf
    #             if saleorderid.state in ['draft']:
    #                 saleorderid.action_confirm()
    #         if status.name == 'Awaiting bank wire payment':
    #             erorra
    #             if saleorderid.state in ['draft']:
    #                 saleorderid.action_confirm()
    #         if status.name == 'Delivered':
    #             if saleorderid.state in ['draft']:
    #                 saleorderid.action_confirm()
    #         if status.name == 'Shipped':
    #             erorrs
    #             if saleorderid.state in ['draft']:
    #                 saleorderid.action_confirm()
    #
    #         #     if saleorderid.state in ['progress', 'done', 'manual']:
    #         #         invoice_ids = saleorderid.invoice_ids
    #         #         for invoice in invoice_ids:
    #         #             refund_ids = invoice_obj.search([('invoice_origin', '=', invoice.number)])
    #         #             if not refund_ids:
    #         #                 if invoice.state == 'paid':
    #         #                     refund_invoice_id = invoice_obj.create(dict(
    #         #                         description='Refund To %s' % (invoice.partner_id.name),
    #         #                         date=datetime.date.today(),
    #         #                         filter_refund='refund'
    #         #                     ))
    #         #                     refund_invoice_id.invoice_refund()
    #         #                     saleorderid.write({'is_refund': True})
    #         #                 else:
    #         #                     invoice.action_cancel()
    #         #
    #         #         for picking in saleorderid.picking_ids:
    #         #             if picking.state not in ('done'):
    #         #                 picking.action_cancel()
    #         #             else:
    #         #                 ctx = self._context.copy()
    #         #                 ctx.update({'active_id': picking.id})
    #         #                 res = return_obj.with_context(ctx).default_get(['product_return_moves', 'move_dest_exists'])
    #         #                 res.update({'invoice_state': '2binvoiced'})
    #         #                 return_id = return_obj.with_context(ctx).create({'invoice_state': 'none'})
    #         #                 for record in res['product_return_moves']:
    #         #                     record.update({'wizard_id': return_id.id})
    #         #                     return_line_obj.with_context(ctx).create(record)
    #         #
    #         #                 pick_id_return, type = return_id.with_context(ctx)._create_returns()
    #         #                 # pick_id_return.force_assign()
    #         #                 pick_id_return._action_done()
    #         #     saleorderid.action_cancel()
    #         #     return True
    #         #
    #         # # Make Order Confirm
    #         # # if validate order is activated in workflow
    #         # if self.workflow_id.validate_order:
    #         #     if saleorderid.state in ['draft']:
    #         #         saleorderid.action_confirm()
    #         #
    #         # # if complete shipment is activated in workflow
    #         # if self.workflow_id.complete_shipment:
    #         #     if saleorderid.state in ['draft', 'confirmed']:
    #         #         saleorderid.action_confirm()
    #         #     for picking_id in saleorderid.picking_ids:
    #         #
    #         #         # If still in draft => confirm and assign
    #         #         if picking_id.state == 'draft':
    #         #             picking_id.action_confirm()
    #         #         # picking_id._action_assign()
    #         #
    #         #         # if picking_id.state == 'confirmed':
    #         #         # picking_id._action_assign()
    #         #         move_ids = picking_id.move_ids_without_package._action_confirm()
    #         #         move_ids._action_assign()
    #         #
    #         # # if create_invoice is activated in workflow
    #         # if self.workflow_id.create_invoice:
    #         #     if not saleorderid.invoice_ids:
    #         #         invoice_ids = saleorderid._create_invoices()
    #         #         invoice_ids.write({'is_prestashop': True})
    #         #
    #         # # if validate_invoice is activated in workflow
    #         # if self.workflow_id.validate_invoice:
    #         #     if saleorderid.state == 'draft':
    #         #         saleorderid.action_confirm()
    #         #
    #         #     if not saleorderid.invoice_ids:
    #         #         invoice_ids = saleorderid._create_invoices()
    #         #         # invoice_ids = invoice_obj.browse(invoice_ids)
    #         #         invoice_ids.write({'is_prestashop': True})
    #         #
    #         #     for invoice_id in saleorderid.invoice_ids:
    #         #         invoice_id.write({
    #         #             'total_discount_tax_excl': self.get_value_data(order_detail.get('total_discounts_tax_excl')),
    #         #             'total_discount_tax_incl': self.get_value_data(order_detail.get('total_discounts_tax_incl')),
    #         #             'total_paid_tax_excl': self.get_value_data(order_detail.get('total_paid_tax_excl')),
    #         #             'total_paid_tax_incl': self.get_value_data(order_detail.get('total_paid_tax_incl')),
    #         #             'total_products_wt': self.get_value_data(order_detail.get('total_products_wt')),
    #         #             'total_shipping_tax_excl': self.get_value_data(order_detail.get('total_shipping_tax_excl')),
    #         #             'total_shipping_tax_incl': self.get_value_data(order_detail.get('total_shipping_tax_incl')),
    #         #             'total_wrapping_tax_excl': self.get_value_data(order_detail.get('total_wrapping_tax_excl')),
    #         #             'total_wrapping_tax_incl': self.get_value_data(order_detail.get('total_wrapping_tax_incl')),
    #         #             'is_prestashop': True,
    #         #         })
    #         #         if invoice_id.state == 'draft':
    #         #             invoice_id.action_post()
    #         #
    #         # # if register_payment is activated in workflow
    #         # if self.workflow_id.register_payment:
    #         #     if saleorderid.state == 'draft':
    #         #         saleorderid.action_confirm()
    #         #     if not saleorderid.invoice_ids:
    #         #         if sum(line.qty_to_invoice for line in saleorderid.order_line) > 0:
    #         #             invoice_ids = saleorderid._create_invoices()
    #         #             invoice_ids.write({'is_prestashop': True})
    #         #             for invoice_id in saleorderid.invoice_ids:
    #         #                 invoice_id.write({
    #         #                     'total_discount_tax_excl': self.get_value_data(
    #         #                         order_detail.get('total_discounts_tax_excl')),
    #         #                     'total_discount_tax_incl': self.get_value_data(
    #         #                         order_detail.get('total_discounts_tax_incl')),
    #         #                     'total_paid_tax_excl': self.get_value_data(order_detail.get('total_paid_tax_excl')),
    #         #                     'total_paid_tax_incl': self.get_value_data(order_detail.get('total_paid_tax_incl')),
    #         #                     'total_products_wt': self.get_value_data(order_detail.get('total_products_wt')),
    #         #                     'total_shipping_tax_excl': self.get_value_data(
    #         #                         order_detail.get('total_shipping_tax_excl')),
    #         #                     'total_shipping_tax_incl': self.get_value_data(
    #         #                         order_detail.get('total_shipping_tax_incl')),
    #         #                     'total_wrapping_tax_excl': self.get_value_data(
    #         #                         order_detail.get('total_wrapping_tax_excl')),
    #         #                     'total_wrapping_tax_incl': self.get_value_data(
    #         #                         order_detail.get('total_wrapping_tax_incl')),
    #         #                     'is_prestashop': True,
    #         #                 })
    #         #                 if invoice_id.state == 'draft':
    #         #                     invoice_id.action_post()
    #         #
    #         #     if saleorderid.invoice_ids:
    #         #         for invoice_id in saleorderid.invoice_ids:
    #         #             if invoice_id.state not in ['paid'] and invoice_id.invoice_line_ids:
    #         #                 payment_register_id = self.env['account.payment.register'].with_context(
    #         #                     active_model='account.move', active_ids=invoice_id.ids).create(
    #         #                     {'journal_id': self.sale_journal.id, 'amount': invoice_id.amount_residual})
    #         #                 payments = payment_register_id.action_create_payments()
    #     return True

    # def manageOrderWorkflow(self, saleorderid, order_detail, status, prestashop):
    #     advance_payment_adjust_obj = self.env['sale.advance.payment.inv']
    #     print("saleorderid+________-", saleorderid.presta_id)
    #     if saleorderid.order_line:
    #         if saleorderid.order_status.confirm_order:
    #             if saleorderid.state not in ('sale', 'done', 'cancel'):
    #                 saleorderid.action_confirm()
    #         if saleorderid.order_status.paid:
    #             if saleorderid.state not in ('sale', 'done', 'cancel'):
    #                 saleorderid.action_confirm()
    #                 saleorderid._create_invoices()
    #                 for invoice_id in saleorderid.invoice_ids:
    #                     invoice_id, invoice_id.action_post()
    #             if saleorderid.invoice_ids:
    #                 unpaid_inv = saleorderid.invoice_ids.filtered(
    #                     lambda inv: inv.payment_state in ('not_paid', ''))
    #                 if unpaid_inv:
    #                     payment = self.env['account.payment.register'].with_context(active_ids=unpaid_inv.ids,
    #                                                                                 active_model='account.move').create(
    #                         {})
    #                     payment.action_create_payments()
    #         if saleorderid.order_status.shipped:
    #             if saleorderid.state not in ('sale', 'done', 'cancel'):
    #                 saleorderid.action_confirm()
    #             for picking_id in saleorderid.picking_ids:
    #                 check_forecast_list = len(picking_id.move_ids_without_package)
    #                 forecast_list = []
    #                 print('check_forecast_list++++++++++++', check_forecast_list)
    #
    #                 for move_id in picking_id.move_ids_without_package:
    #                     if move_id.product_uom_qty <= move_id.product_id.virtual_available:
    #                         move_id.write({
    #                             'quantity_done': move_id.product_uom_qty
    #                         })
    #                         forecast_list.append(1)
    #                     elif move_id.product_id.type == 'consu':
    #                         move_id.write({
    #                             'quantity_done': move_id.product_uom_qty
    #                         })
    #                         forecast_list.append(1)
    #                 print('forecast_list++++++++++++', forecast_list)
    #                 if len(forecast_list) == check_forecast_list:
    #                     if picking_id.state not in ['done', 'cancel']:
    #                         if picking_id.state == 'assigned':
    #                             picking_id.with_context(skip_backorder=True, skip_sms=True,
    #                                                     skip_immediate=True).button_validate()
    #                         else:
    #                             print("Product is not available to validate+__________________")
    #                             msg = 'Product is not available to validate'
    #                             log_id_obj = self.env['prestashop.log'].create(
    #                                 {'all_operations': 'import_orders',
    #                                  'error_lines': [(0, 0, {'log_description': str(msg),
    #                                                          'prestashop_id': saleorderid.presta_id})]})
    #                             print("log_id_obj+_____________", log_id_obj)
    #                             log_id = log_id_obj.id
    #                             print("log_id_++++++", log_id)
    #                             new_context = dict(self.env.context)
    #                             new_context.update({'log_id': log_id})
    #                             self.env.context = new_context
    #
    #             if 2 > len(saleorderid.invoice_ids) and saleorderid.invoice_status != 'invoiced':
    #                 saleorderid._create_invoices()
    #                 for invoice_id in saleorderid.invoice_ids:
    #                     invoice_id, invoice_id.action_post()
    #                 # invoice = advance_payment_adjust_obj.create({'advance_payment_method': 'delivered'})
    #                 # print("invoice+____________________________-",invoice)
    #                 # print("invoice+____________________________-",invoice.with_context(active_ids=saleorderid.ids))
    #                 # invoice.with_context(active_ids=saleorderid.ids).create_invoices()
    #                 # saleorderid.invoice_ids.filtered(lambda r: r.state == 'draft').action_post()
    #     return True

    def manageOrderWorkflow(self, saleorderid, order_detail, status, prestashop):
        advance_payment_adjust_obj = self.env['sale.advance.payment.inv']
        print("saleorderid+________-", saleorderid.presta_id)
        if saleorderid.order_line:
            if saleorderid.order_status.confirm_order:
                if saleorderid.state not in ('sale', 'done', 'cancel'):
                    saleorderid.action_confirm()
            if saleorderid.order_status.paid:
                if saleorderid.state not in ('sale', 'done', 'cancel'):
                    saleorderid.action_confirm()
                    saleorderid._create_invoices()
                    for invoice_id in saleorderid.invoice_ids:
                        invoice_id, invoice_id.action_post()
                if saleorderid.invoice_ids:
                    unpaid_inv = saleorderid.invoice_ids.filtered(
                        lambda inv: inv.payment_state in ('not_paid', ''))
                    if unpaid_inv:
                        payment = self.env['account.payment.register'].with_context(active_ids=unpaid_inv.ids,
                                                                                    active_model='account.move').create(
                            {})
                        payment.action_create_payments()
            if saleorderid.order_status.shipped:
                if saleorderid.state not in ('sale', 'done', 'cancel'):
                    saleorderid.action_confirm()
                for picking_id in saleorderid.picking_ids:
                    picking_id.action_assign()
                    if picking_id.state == "assigned":
                        for move in picking_id.move_ids.filtered(
                            lambda m: m.state not in ["done", "cancel"]
                        ):
                            rounding = move.product_id.uom_id.rounding
                            if (
                                float_compare(
                                    move.quantity_done,
                                    move.product_qty,
                                    precision_rounding=rounding,
                                )
                                == -1
                            ):
                                for move_line in move.move_line_ids:
                                    move_line.qty_done = move_line.reserved_uom_qty
                        picking_id.with_context(skip_immediate=True, skip_sms=True).button_validate()
                        if not picking_id.state in ['done', 'cancel']:
                            msg = 'Product is not available to validate'
                            log_id_obj = self.env['prestashop.log'].create(
                                {'all_operations': 'import_orders',
                                 'error_lines': [
                                     (
                                         0, 0, {'log_description': str(msg), 'prestashop_id': saleorderid.name})]})
                            log_id = log_id_obj.id
                            new_context = dict(self.env.context)
                            new_context.update({'log_id': log_id})
                            self.env.context = new_context

                    else:
                        picking_id.state in ('confirmed', 'waiting', 'assigned')
                        if picking_id._get_without_quantities_error_message():
                            msg = (
                                'You cannot validate a transfer if no quantities are reserved nor done. '
                                'To force the transfer, switch in edit mode and encode the done quantities.'
                            )
                            log_id_obj = self.env['prestashop.log'].create(
                                {'all_operations': 'import_orders',
                                 'error_lines': [
                                     (
                                         0, 0, {'log_description': str(msg), 'prestashop_id': saleorderid.name})]})
                            log_id = log_id_obj.id
                            new_context = dict(self.env.context)
                            new_context.update({'log_id': log_id})
                            self.env.context = new_context
                        else:
                            msg = 'Product is not available to validate'
                            log_id_obj = self.env['prestashop.log'].create(
                                {'all_operations': 'import_orders',
                                 'error_lines': [
                                     (
                                         0, 0, {'log_description': str(msg), 'prestashop_id': saleorderid.presta_id})]})
                            log_id = log_id_obj.id
                            new_context = dict(self.env.context)
                            new_context.update({'log_id': log_id})
                            self.env.context = new_context
                if 2 > len(saleorderid.invoice_ids) and saleorderid.invoice_status != 'invoiced':
                    saleorderid._create_invoices()
                    for invoice_id in saleorderid.invoice_ids:
                        invoice_id, invoice_id.action_post()
                    # invoice = advance_payment_adjust_obj.create({'advance_payment_method': 'delivered'})
                    # print("invoice+____________________________-",invoice)
                    # print("invoice+____________________________-",invoice.with_context(active_ids=saleorderid.ids))
                    # invoice.with_context(active_ids=saleorderid.ids).create_invoices()
                    # saleorderid.invoice_ids.filtered(lambda r: r.state == 'draft').action_post()
        return True

    # @api.one
    def manageOrderLines(self, orderid, order_detail, prestashop):
        sale_order_line_obj = self.env['sale.order.line']
        prod_attr_val_obj = self.env['product.attribute.value']
        prod_templ_obj = self.env['product.template']
        product_obj = self.env['product.product']
        tax_rule_obj = self.env['prestashop.tax.rule']
        lines = []
        order_rows = order_detail.get('associations').get('order_rows').get('order_row')
        if order_rows is not None:
            if isinstance(order_rows, list):
                order_rows = order_rows
            else:
                order_rows = [order_rows]
            for child in order_rows:
                line = {
                    'price_unit': float(self.get_value_data(child.get('unit_price_tax_excl'))),
                    'name': self.get_value_data(child.get('product_name')),
                    'product_uom_qty': float(self.get_value_data(child.get('product_quantity'))),
                    'order_id': orderid.id,
                    'tax_id': False,
                    'presta_id': self.get_value_data(child.get('id')),
                    'presta_line': True,
                }
                group_tax_id = False
                if self.get_value_data(child.get('product_attribute_id')) != '0':
                    value_list = []
                    temp_id = False
                    try:
                        combination = prestashop.get('combinations',
                                                     self.get_value_data(child.get('product_attribute_id')))
                        value_ids = combination.get('combination').get('associations').get('product_option_values').get(
                            'product_option_value')
                        if isinstance(value_ids, list):
                            value_ids = value_ids
                        else:
                            value_ids = [value_ids]
                        for value_id in value_ids:
                            values = self.get_value_data(value_id.get('id'))
                            value_ids = prod_attr_val_obj.search([('presta_id', '=', values)])
                            value_list.append(value_ids.id)
                        temp_id = prod_templ_obj.search(
                            [('presta_id', '=', self.get_value_data(child.get('product_id'))),
                             ('prestashop_product', '=', True)], limit=1)
                    except Exception as e:
                        logger.info('Error/Warning product combination 000000000000000000000000000===> %s', e)
                    if not temp_id:
                        try:
                            prod_data_tmpl = prestashop.get('products', self.get_value_data(child.get('product_id')))
                            self.create_presta_product(prod_data_tmpl.get('product'), prestashop)
                            temp_id = prod_templ_obj.search(
                                [('presta_id', '=', self.get_value_data(child.get('product_id'))),
                                 ('prestashop_product', '=', True)], limit=1)
                        except Exception as e:
                            logger.info('Error/Warning product combination 11111111111111111111111111111111111===> %s',
                                        e)
                    if temp_id:
                        print('\ntemp_id++++', temp_id)
                        print('\nchild id from prests++++', child)
                        print('\nchild product id from prests++++', self.get_value_data(child.get('product_id')))
                        product_ids = product_obj.search(
                            [('product_tmpl_id.presta_id', '=', self.get_value_data(child.get('product_id')))])
                        print('\nproduct_ids+++before+', product_ids)
                        for product_id in product_ids:
                            if product_id.product_template_attribute_value_ids == prod_attr_val_obj.browse(
                                value_list) and product_id.product_tmpl_id == temp_id:
                                product_ids = product_id

                        if product_ids:
                            group_tax_id = product_ids[0].tax_group_id
                            line.update({'product_id': product_ids[0].id, 'product_uom': product_ids[0].uom_id.id})
                        else:
                            prod_data = prestashop.get('products', self.get_value_data(child.get('product_id')))
                            self.create_presta_product(prod_data.get('product'), prestashop)
                            product_ids = product_obj.search([('product_tmpl_id.presta_id', '=',
                                                               self.get_value_data(child.get('product_attribute_id')))])

                            print('\nproduct_ids+++++++++++', product_ids)

                            group_tax_id = product_ids[0].tax_group_id
                            line.update({'product_id': product_ids[0].id, 'product_uom': product_ids[0].uom_id.id})
                else:
                    product_id = product_obj.search(
                        [('product_tmpl_id.presta_id', '=', self.get_value_data(child.get('product_id'))),
                         ('prestashop_product', '=', True)], limit=1)
                    if product_id:
                        group_tax_id = product_id.tax_group_id
                        line.update({'product_id': product_id.id, 'product_uom': product_id.uom_id.id})
                    else:
                        try:
                            new_product_data = prestashop.get('products', self.get_value_data(child.get('product_id')))
                            self.create_presta_product(new_product_data.get('product'), prestashop)
                            self.env.cr.commit()
                            new_product_ids = product_obj.search(
                                [('product_tmpl_id.presta_id', '=', self.get_value_data(child.get('product_id')))])
                            group_tax_id = new_product_ids[0].tax_group_id
                            line.update(
                                {'product_id': new_product_ids[0].id, 'product_uom': new_product_ids[0].uom_id.id})
                        except:
                            product_id = self.remove_record_prestashop_checked(prod_templ_obj, 'Removed Product',
                                                                               {'name': 'Removed Product'})
                            group_tax_id = product_id.tax_group_id
                            line.update({'product_id': product_id.id, 'product_uom': product_id.uom_id.id})
                if 'product_id' not in line:
                    product_id = self.remove_record_prestashop_checked(prod_templ_obj, 'Removed Product',
                                                                       {'name': 'Removed Product'})
                    line.update({'product_id': product_id.id, 'product_uom': product_id.uom_id.id})
                if group_tax_id and self.get_value_data(child.get('unit_price_tax_excl')) != self.get_value_data(
                    child.get('unit_price_tax_incl')):
                    tax_rule_id = tax_rule_obj.search([('group_id', '=', group_tax_id.id)], limit=1)
                    line.update({'tax_id': [(6, 0, tax_rule_id.tax_id.ids)]})
                line_ids = sale_order_line_obj.search(
                    [('presta_id', '=', line.get('presta_id')), ('order_id', '=', orderid.id)], limit=1)
                if not line_ids:
                    sale_order_line_obj.create(line)
                else:
                    line_ids.write(line)

        if order_detail.get('total_discounts'):
            discoun = order_detail.get('total_discounts_tax_incl')
            discount_line = {
                'product_id': self.discount_product_id.id,
                'product_uom': self.discount_product_id.uom_id.id,
                'price_unit': - (float(discoun)),
                'product_uom_qty': 1,
                'tax_id': False,
                'order_id': orderid.id
            }
        dline_ids = sale_order_line_obj.search(
            [('product_id', '=', self.get_value_data(discount_line.get('product_id'))), ('order_id', '=', orderid.id)])
        if not dline_ids:
            sale_order_line_obj.create(dline_ids)
        else:
            dline_ids[0].write({'price_unit': - (float(discoun))})
        # Shipment fees and fields
        ship = float(self.get_value_data(order_detail.get('total_shipping_tax_incl')))
        if ship and ship > 0:
            sline = {
                'product_id': self.shipment_fee_product_id.id,
                'product_uom': self.shipment_fee_product_id.uom_id.id,
                'price_unit': ship,
                'product_uom_qty': 1,
                'order_id': orderid.id,
                'tax_id': False,
            }
            sline_ids = sale_order_line_obj.search(
                [('product_id', '=', self.get_value_data(sline.get('product_id'))), ('order_id', '=', orderid.id)])
            if not sline_ids:
                sale_order_line_obj.create(sline)
            else:
                sline_ids[0].write(sline)

        # wrapping fees and fields
        wrapping = float(self.get_value_data(order_detail.get('total_wrapping', 0)))
        if wrapping and wrapping > 0:
            wline = {
                'product_id': self.gift_wrapper_fee_product_id.id,
                'product_uom': self.gift_wrapper_fee_product_id.uom_id.id,
                'price_unit': wrapping,
                'product_uom_qty': 1,
                'name': self.get_value_data(order_detail.get('gift_message')),
                'order_id': orderid.id,
                'tax_id': False,
            }
            wline_ids = sale_order_line_obj.search(
                [('product_id', '=', self.get_value_data(wline.get('product_id'))), ('order_id', '=', orderid.id)])
            if not wline_ids:
                sale_order_line_obj.create(wline)
            else:
                wline_ids[0].write(wline)

    # @api.one

    def remove_record_prestashop_checked(self, brows_object, name, vals):
        print('brows_object++++++++', brows_object)
        print('name++++++++', name)
        print('vals++++++++', vals)
        record_id = brows_object.search([('name', '=', name)], limit=1)
        print('record_id++++++++++', record_id)
        if not record_id:
            record_id = brows_object.create(vals)
            print('record_id++++++++', record_id)
            self.env.cr.commit()
        return record_id

    def create_presta_order(self, order_detail, prestashop):
        sale_order_obj = self.env['sale.order']
        res_partner_obj = self.env['res.partner']
        carrier_obj = self.env['delivery.carrier']
        product_obj = self.env['product.product']
        status_obj = self.env['presta.order.status']
        order_vals = {}
        # try:
        id_customer = res_partner_obj.search(
            [('presta_id', '=', order_detail.get('id_customer')), ('prestashop_customer', '=', True)], limit=1)
        if not id_customer:
            # try:
            cust_data = prestashop.get('customers', order_detail.get('id_customer'))
            id_customer = self.create_customer(cust_data.get('customer'), prestashop)
            # except Exception as e:
            #     id_customer = self.remove_record_prestashop_checked(res_partner_obj, 'Removed Customer',
            #                                                         {'name': 'Removed Customer'})
        id_address_delivery = res_partner_obj.search(
            [('presta_id', '=', order_detail.get('id_address_delivery')), ('prestashop_address', '=', True)],
            limit=1)
        if not id_address_delivery:
            # try:
            address_data = prestashop.get('addresses', order_detail.get('id_address_delivery'))
            id_address_delivery = self.create_address(address_data.get('address'), prestashop)
            # except Exception as e:
            #     id_address_delivery = self.remove_record_prestashop_checked(res_partner_obj, 'Removed Addresss',
            #                                                                 {'name': 'Removed Addresss'})
        id_address_invoice = res_partner_obj.search(
            [('presta_id', '=', order_detail.get('id_address_invoice')), ('prestashop_address', '=', True)],
            limit=1)
        if not id_address_invoice:
            # try:
            address_inv_data = prestashop.get('addresses', order_detail.get('id_address_invoice'))
            id_address_invoice = self.create_address(address_inv_data.get('address'), prestashop)
            # except Exception as e:
            #     id_address_invoice = self.remove_record_prestashop_checked(res_partner_obj, 'Removed Addresss',
            #                                                                {'name': 'Removed Addresss'})
        order_vals.update({'partner_id': id_customer.id, 'partner_shipping_id': id_address_delivery.id,
                           'partner_invoice_id': id_address_invoice.id})
        state_id = status_obj.search([('presta_id', '=', self.get_value_data(order_detail.get('current_state')))],
                                     limit=1)
        print("\nstate_id_+++++++++++++++++++++", state_id)
        # if not state_id:
        #     # try:
        #     orders_status_lst = prestashop.get('order_states',
        #                                        self.get_value_data(order_detail.get('current_state')))
        #
        #     print("orders_status_lst_+_++_+__+_++_+_",orders_status_lst)
        #     state_id = status_obj.create({'name': self.get_value_data(
        #         self.get_value(orders_status_lst.get('order_state').get('name').get('language'))),
        #         'presta_id': self.get_value_data(
        #             order_detail.get('current_state')), })
        #     print("state_id+_+_+_+_+_+_+_+_+_+_", state_id)
        # except Exception as e:
        #     state_id = self.remove_record_prestashop_checked(status_obj, 'Removed Status',
        #                                                      {'name': 'Removed Status'})

        a = self.get_value_data(order_detail.get('payment'))
        p_mode = False
        if a == 'Cash on delivery  COD':
            p_mode = 'cod'
        elif a == 'Bank wire':
            p_mode = 'bankwire'
        elif a == 'Payments by check':
            p_mode = 'cheque'
        elif a == 'Bank transfer':
            p_mode = 'banktran'
        order_vals.update({
            'reference': self.get_value_data(order_detail.get('reference')),
            'presta_id': order_detail.get('id'),
            'warehouse_id': self.warehouse_id.id,
            'presta_order_ref': self.get_value_data(order_detail.get('reference')),
            'pretsa_payment_mode': p_mode,
            'pricelist_id': self.pricelist_id.id,
            'workflow_order_id': self.workflow_id.id,
            # 'name':  self.get_value_data(order_detail.get('id')),
            'order_status': state_id.id,
            'shop_id': self.id,
            'prestashop_order': True,
            'prestashops_order': True,
            'presta_order_date': self.get_value_data(order_detail.get('date_add')),
        })
        if self.workflow_id.picking_policy:
            order_vals.update({'picking_policy': self.workflow_id.picking_policy})
        carr_id = False
        if int(self.get_value_data(order_detail.get('id_carrier'))) > 0:
            carr_obj_id = carrier_obj.search(
                [('presta_id', '=', order_detail.get('id_carrier')), ('is_presta', '=', True)], limit=1)
            if carr_obj_id:
                carr_id = carr_obj_id.id
            if not carr_obj_id:
                try:
                    carrier_data = prestashop.get('carriers', self.get_value_data(order_detail.get('id_carrier')))
                    carr_id = self.create_carrier(self.get_value_data(carrier_data.get('carrier')))
                except Exception as e:
                    product_id = self.remove_record_prestashop_checked(product_obj, 'Removed Carrier',
                                                                       {'name': 'Removed Carrier'})
                    carr_id = self.remove_record_prestashop_checked(carrier_obj, 'Removed Carrier',
                                                                    {'name': 'Removed Carrier',
                                                                     'product_id': product_id.id,
                                                                     'is_presta': True}).id
            order_vals.update({'carrier_prestashop': carr_id})
        sale_order_id = sale_order_obj.search(
            [('presta_id', '=', order_detail.get('id')), ('prestashop_order', '=', True)], limit=1)
        if not sale_order_id:
            sale_order_id = sale_order_obj.create(order_vals)
            logger.info('created orders ===> %s', sale_order_id.id)
        if sale_order_id:
            self.env.cr.execute(
                "select saleorder_id from saleorder_shop_rel where saleorder_id = %s and shop_id = %s" % (
                    sale_order_id.id, self.id))
            so_data = self.env.cr.fetchone()
            if so_data == None:
                self.env.cr.execute("insert into saleorder_shop_rel values(%s,%s)" % (sale_order_id.id, self.id))
        print("sale_order_id+_+_+_+_+_+_+_+_+_", sale_order_id)
        self.manageOrderLines(sale_order_id, order_detail, prestashop)
        self.manageOrderWorkflow(sale_order_id, order_detail, state_id, prestashop)
        self.env.cr.commit()
        return sale_order_id
        # except Exception as e:
        # if self.env.context.get('log_id'):
        #     log_id = self.env.context.get('log_id')
        #     self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
        # else:
        #     log_id_obj = self.env['prestashop.log'].create(
        #         {'all_operations': 'import_orders', 'error_lines': [(0, 0, {'log_description': str(e)})]})
        #     log_id = log_id_obj.id
        # self = self.with_context(log_id = log_id.id)
        # new_context = dict(self.env.context)
        # new_context.update({'log_id': log_id})
        # self.env.context = new_context
        return True

    def import_orders(self):
        # try:
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            filters = {'display': 'full', 'filter[id]': '>[%s]' % shop.last_order_id_id_import,
                       'filter[id_shop]': '%s' % self.presta_id, 'limit': 100}
            prestashop_order_data = prestashop.get('orders', options=filters)
            print('\nlren+++++++++++++++++++', len(prestashop_order_data))
            print('\n++++++++++++++++++', prestashop_order_data)
            if prestashop_order_data.get('orders') and prestashop_order_data.get('orders').get('order'):
                orders = prestashop_order_data.get('orders').get('order')
                if isinstance(orders, list):
                    orders = orders
                else:
                    orders = [orders]
                for order in orders:
                    shop.create_presta_order(order, prestashop)
                    shop.write({'last_order_id_id_import': order.get('id')})
                self.env.cr.commit()
        # except Exception as e:
        #     raise ValidationError(_(str(e)))
        return True

    def import_orders_status(self):
        # try:
        status_obj = self.env['presta.order.status']
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            filters = {'display': 'full', 'filter[id]': '>[%s]' % 0, 'limit': 1000}
            prestashop_order_status_data = prestashop.get('order_states', options=filters)
            if prestashop_order_status_data.get('order_states') and prestashop_order_status_data.get(
                'order_states').get('order_state'):
                order_status = prestashop_order_status_data.get('order_states').get('order_state')
                if isinstance(order_status, list):
                    order_status = order_status
                else:
                    order_status = [order_status]
                for order_status_dict in order_status:
                    state_id = status_obj.search([('presta_id', '=', self.get_value_data(order_status_dict.get('id')))],
                                                 limit=1)
                    if not state_id:
                        status_obj.create(
                            {'name': self.get_value_data(self.get_value(order_status_dict.get('name').get('language'))),
                             'presta_id': self.get_value_data(order_status_dict.get('id'))})
            else:
                raise ValidationError(_('Imported all status'))

    def create_presta_message_threads(self, thread, prestashop):
        res_obj = self.env['res.partner']
        sale_obj = self.env['sale.order']
        customer_threads_obj = self.env['customer.threads']
        thread_id = customer_threads_obj.search([('presta_id', '=', thread)], limit=1)
        if not thread_id:
            try:
                customer_threads = prestashop.get('customer_threads', thread)
                if customer_threads.get('customer_thread'):
                    customer_thread_dict = customer_threads.get('customer_thread')
                    threads_vals = {
                        'presta_id': customer_thread_dict.get('id'),
                        'id_shop': self.get_value_data(customer_thread_dict.get('id_shop')),
                        'token': self.get_value_data(customer_thread_dict.get('token')),
                        'email': self.get_value_data(customer_thread_dict.get('email')),
                        'status': self.get_value_data(customer_thread_dict.get('status')),
                    }
                    if self.get_value_data(customer_thread_dict.get('id_customer')):
                        customer_id = res_obj.search(
                            [('presta_id', '=', self.get_value_data(customer_thread_dict.get('id_customer'))),
                             ('prestashop_customer', '=', True)], limit=1)
                        if not customer_id:
                            try:
                                cust_data = prestashop.get('customers',
                                                           self.get_value_data(customer_thread_dict.get('id_customer')))
                                customer_id = self.create_customer(cust_data.get('customer'), prestashop)
                            except Exception as e:
                                customer_id = self.remove_record_prestashop_checked(res_obj, 'Removed Customer',
                                                                                    {'name': 'Removed Customer'})
                        threads_vals.update({'customer_id': customer_id.id, })
                    order_presta_id = self.get_value_data(customer_thread_dict.get('id_order'))
                    if order_presta_id:
                        check_order = True
                        order = sale_obj.search([('presta_id', '=', order_presta_id), ('prestashop_order', '=', True)],
                                                limit=1)
                        if not order:
                            try:
                                order_detail = prestashop.get('orders',
                                                              self.get_value_data(customer_thread_dict.get('id_order')))
                                order_data_ids = order_detail.get('order')
                                order = self.create_presta_order(order_data_ids, prestashop)
                            except Exception as e:
                                check_order = False
                        if check_order:
                            threads_vals.update({'order_id': order.id})
                    thread_id = customer_threads_obj.create(threads_vals)
            except Exception as e:
                thread_id = False
        return thread_id

    def create_presta_message(self, message_dict, prestashop):
        order_msg = self.env['order.message']
        order_msg_vals = {
            'msg_prest_id': self.get_value_data(message_dict.get('id')),
            'message': self.get_value_data(message_dict.get('message')),
        }
        thread_id = self.create_presta_message_threads(message_dict.get('id_customer_thread'), prestashop)
        if thread_id != False:
            order_msg_vals.update({'thread_id': thread_id.id, 'new_id': thread_id.order_id.id})
            order_msg_id = order_msg.search(
                [('thread_id', '=', thread_id.id), ('msg_prest_id', '=', order_msg_vals.get('msg_prest_id'))])
            if not order_msg_id:
                msg_id = order_msg.create(order_msg_vals)
                logger.info('created messages ===> %s', msg_id.id)
                self.env.cr.commit()
            else:
                order_msg_id.write(order_msg_vals)

    def import_messages(self):
        try:
            for shop in self:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '=[%s]' % shop.last_message_id_import,
                           'filter[id_shop]': '%s' % self.presta_id, 'limit': 20}
                message = prestashop.get('customer_messages', options=filters)
                if message.get('customer_messages') and message.get('customer_messages').get('customer_message'):
                    messages = message.get('customer_messages').get('customer_message')
                    if isinstance(messages, list):
                        messages = messages
                    else:
                        messages = [messages]
                    for message_dict in messages:
                        shop.create_presta_message(message_dict, prestashop)
                        shop.write({'last_message_id_import': message_dict.get('id')})

        except Exception as e:
            raise ValidationError(_(str(e)))
        return True

    # @api.multi
    def import_cart_rules(self):
        try:
            cart_obj = self.env['cart.rules']
            res_partner_obj = self.env['res.partner']
            for shop in self:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'limit': 500}
                cart = prestashop.get('cart_rules', options=filters)
                print("cart_++++++++++++++++++", cart)
                if cart.get('cart_rules') and cart.get('cart_rules').get('cart_rule'):
                    carts = cart.get('cart_rules').get('cart_rule')
                    if isinstance(carts, list):
                        carts = carts
                    else:
                        carts = [carts]
                    for cart_dict in carts:
                        print("\ncart_dict+_________________-", cart_dict)
                        id_customer = self.env['res.partner'].search([('presta_id', '=', cart_dict.get('id_customer'))])
                        print("id_customer_++++++++++++", id_customer)
                        if not id_customer:
                            try:
                                cust_data = prestashop.get('customers', cart_dict.get('id_customer'))
                                id_customer = shop.create_customer(cust_data.get('customer'), prestashop)
                            except Exception as e:
                                id_customer = self.remove_record_prestashop_checked(res_partner_obj, 'Removed Customer',
                                                                                    {'name': 'Removed Customer'})
                        cart_vals = {
                            'id_customer': id_customer.id or False,
                            'date_from': self.get_value_data(cart_dict.get('date_from')),
                            'date_to': self.get_value_data(cart_dict.get('date_to')),
                            'description': self.get_value_data(cart_dict.get('description')),
                            'quantity': self.get_value_data(cart_dict.get('quantity')),
                            'code': self.get_value_data(cart_dict.get('code')),
                            'partial_use': bool(int(self.get_value_data(cart_dict.get('partial_use')))),
                            'minimum_amount': self.get_value_data(cart_dict.get('minimum_amount')),
                            'free_shipping': bool(int(self.get_value_data(cart_dict.get('free_shipping')))),
                            # 'name' : cart_data.get('cart_rule').get('name').get('language').get('value'),
                            'name': self.get_value_data(self.get_value(cart_dict.get('name').get('language'))),
                            'presta_id': cart_dict.get('id'),
                        }
                        print("cart_vals_+++++++++++", cart_vals)
                        carts_id = cart_obj.search([('presta_id', '=', self.get_value_data(cart_dict.get('id')))],
                                                   limit=1)
                        if not carts_id:
                            carts_id = cart_obj.create(cart_vals)

                        else:
                            carts_id.write(cart_vals)
                        self.env.cr.execute("select cart_id from cart_shop_rel where cart_id = %s and shop_id = %s" % (
                            carts_id.id, shop.id))
                        data = self.env.cr.fetchone()
                        if not data:
                            self.env.cr.execute("insert into cart_shop_rel values(%s,%s)" % (carts_id.id, shop.id))
                        self.env.cr.commit()
                        shop.write({'last_catalog_rule_id_import': cart_dict.get('id')})
                        # shop.write({'last_order_id_id_import': order.get('id')})
                        self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_cart_rules', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return True

    def import_catalog_price_rules(self):
        try:
            catalog_price_obj = self.env['catalog.price.rules']
            for shop in self:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                filters = {'display': 'full', 'filter[id]': '=[%s]' % shop.last_catalog_rule_id_import,
                           'filter[id_shop]': '%s' % self.presta_id, 'limit': 500}
                catalog_rule = prestashop.get('specific_price_rules', options=filters)
                if catalog_rule.get('specific_price_rules') and catalog_rule.get('specific_price_rules').get(
                    'specific_price_rule'):
                    catalog_rules = catalog_rule.get('specific_price_rules').get('specific_price_rule')
                    if isinstance(catalog_rules, list):
                        catalog_rules = catalog_rules
                    else:
                        catalog_rules = [catalog_rules]
                    for catlog_dict in catalog_rules:
                        from_date = False
                        if not self.get_value_data(catlog_dict.get('from')) == '0000-00-00 00:00:00':
                            from_date = self.get_value_data(catlog_dict.get('from'))
                        to_date = False
                        if not self.get_value_data(catlog_dict.get('to')) == '0000-00-00 00:00:00':
                            to_date = self.get_value_data(catlog_dict.get('to'))
                        rule_vals = {
                            'name': self.get_value_data(catlog_dict.get('name')),
                            'from_quantity': self.get_value_data(catlog_dict.get('from_quantity')),
                            'price': self.get_value_data(catlog_dict.get('price')),
                            'reduction': self.get_value_data(catlog_dict.get('reduction')),
                            'reduction_type': self.get_value_data(catlog_dict.get('reduction_type')),
                            'from_date': from_date,
                            'to_date': to_date,
                            'presta_id': catlog_dict.get('id'),
                        }
                        rule_id = catalog_price_obj.search(
                            [('presta_id', '=', self.get_value_data(catlog_dict.get('id')))], limit=1)
                        if not rule_id:
                            rule_id = catalog_price_obj.create(rule_vals)
                            logger.info('created catalog RULE ===> %s', rule_id.id)
                        else:
                            rule_id.write(rule_vals)
                        self.env.cr.execute(
                            "select catalog_id from catalog_shop_rel where catalog_id = %s and shop_id = %s" % (
                                rule_id.id, shop.id))
                        data = self.env.cr.fetchone()
                        if not data:
                            self.env.cr.execute("insert into catalog_shop_rel values(%s,%s)" % (rule_id.id, shop.id))
                    shop.write({'last_catalog_rule_id_import': catlog_dict.get('id')})
                    self.env.cr.commit()
        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'import_catalog_rules', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context
        return True

    # @api.multi
    def update_prestashop_category(self):
        categ_obj = self.env['product.category']
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            try:
                categ_ids = categ_obj.search([('to_be_exported', '=', True), ('shop_ids', '=', shop.id)])
                for each in categ_ids:
                    cat = prestashop.get('categories', each.presta_id)
                    cat.get('category').update({
                        'id': each.presta_id,
                        'name': {'language': {'attrs': {'id': '1'}, 'value': str(each.name)}},
                        'active': 1,
                        'id_parent': each.parent_id and str(each.parent_id.presta_id) or 0,
                    })

                    cat.get('category').pop('level_depth')
                    cat.get('category').pop('nb_products_recursive')
                    result = prestashop.edit('categories', cat)
            except Exception as e:
                if self.env.context.get('log_id'):
                    log_id = self.env.context.get('log_id')
                    self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
                else:
                    log_id_obj = self.env['prestashop.log'].create(
                        {'all_operations': 'update_categories', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                    log_id = log_id_obj.id
                new_context = dict(self.env.context)
                new_context.update({'log_id': log_id})
                self.env.context = new_context
            shop.write({'prestashop_last_update_category_date': datetime.now()})
        return True

    # @api.multi
    def update_cart_rules(self):
        cart_obj = self.env['cart.rules']
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            try:
                query = "select cart_id from cart_shop_rel where shop_id = %s" % shop.id
                self.env.cr.execute(query)
                fetch_cart_rules = self.env.cr.fetchall()
                if fetch_cart_rules != None:
                    fetch_cart_rules = [i[0] for i in fetch_cart_rules]
                    if shop.prestashop_last_update_cart_rule_date:
                        cart_ids = cart_obj.search([('write_date', '>=', shop.prestashop_last_update_cart_rule_date),
                                                    ('id', 'in', fetch_cart_rules)])
                    else:
                        cart_ids = cart_obj.search([('id', 'in', fetch_cart_rules)])

                    for each in cart_ids:
                        # try:
                        cart = prestashop.get('cart_rules', each.presta_id)
                        cart.get('cart_rule').update(
                            {
                                'id': each.presta_id and str(each.presta_id),
                                'code': each.code and str(each.code),
                                'description': each.description and str(each.description),
                                'free_shipping': each.free_shipping and str(int(each.free_shipping)),
                                'id_customer': each.id_customer and each.id_customer.presta_id and str(
                                    each.id_customer.presta_id) or '0',
                                'date_to': str(each.date_to) or '0000-00-00 00:00:00',
                                'name': {'language': {'attrs': {'id': '1'}, 'value': each.name and str(each.name)}},
                                'date_from': str(each.date_from) or '0000-00-00 00:00:00',
                                'partial_use': each.partial_use and str(int(each.partial_use)),
                                'quantity': str(each.quantity),
                            })
                        prestashop.edit('cart_rules', cart)
            except Exception as e:
                if self.env.context.get('log_id'):
                    log_id = self.env.context.get('log_id')
                    self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
                else:
                    log_id_obj = self.env['prestashop.log'].create(
                        {'all_operations': 'update_cart_rules', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                    log_id = log_id_obj.id
                new_context = dict(self.env.context)
                new_context.update({'log_id': log_id})
                self.env.context = new_context
            shop.write({'prestashop_last_update_cart_rule_date': datetime.now()})
        return True

    # @api.multi
    def update_catalog_rules(self):
        catalog_price_obj = self.env['catalog.price.rules']
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            try:
                query = "select catalog_id from catalog_shop_rel where shop_id = %s" % shop.id
                self.env.cr.execute(query)
                fetch_catalog_rules = self.env.cr.fetchall()
                if fetch_catalog_rules is not None:
                    fetch_catalog_rules = [i[0] for i in fetch_catalog_rules]
                    if shop.prestashop_last_update_catalog_rule_date:
                        catalog_ids = catalog_price_obj.search(
                            [('write_date', '>', shop.prestashop_last_update_catalog_rule_date),
                             ('id', 'in', fetch_catalog_rules)])
                    else:
                        catalog_ids = catalog_price_obj.search([('id', 'in', fetch_catalog_rules)])
                    for each in catalog_ids:
                        catalog = prestashop.get('specific_price_rules', each.presta_id)
                        catalog.get('specific_price_rule').update({
                            'id': str(each.presta_id),
                            'reduction_type': str(each.reduction_type),
                            'name': str(each.name),
                            'price': str(each.price),
                            'from_quantity': str(each.from_quantity),
                            'reduction': str(each.reduction),
                            'from': str(each.from_date) or '0000-00-00 00:00:00',
                            'to': str(each.to_date) or '0000-00-00 00:00:00',
                            'id_shop': 1,
                            'id_country': 0,
                            'id_currency': 0,
                            'id_group': 0,
                            'reduction_tax': 0
                        })
                        prestashop.edit('specific_price_rules', catalog)
            except Exception as e:
                if self.env.context.get('log_id'):
                    log_id = self.env.context.get('log_id')
                    self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
                else:
                    log_id_obj = self.env['prestashop.log'].create({'all_operations': 'update_catalog_rules',
                                                                    'error_lines': [
                                                                        (0, 0, {'log_description': str(e), })]})
                    log_id = log_id_obj.id
                new_context = dict(self.env.context)
                new_context.update({'log_id': log_id})
                self.env.context = new_context
            shop.write({'prestashop_last_update_catalog_rule_date': datetime.now()})
        return True

    # @api.multi
    def update_products(self, variant=False):
        # update product details,image and variants
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        category_obj = self.env['product.category']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            query = "select product_id from product_templ_shop_rel_ where shop_id = %s" % shop.id
            self.env.cr.execute(query)
            fetch_products = self.env.cr.fetchall()
            if fetch_products is not None:
                fetch_products = [i[0] for i in fetch_products]
                # if shop.prestashop_last_update_product_data_date:
                #     print('if+++++++++++++++', shop.prestashop_last_update_product_data_date)
                #
                #     product_data_ids = prod_templ_obj.search(
                #         [('write_date', '>', shop.prestashop_last_update_product_data_date),
                #          ])
                #     # ('id', 'in', fetch_products)])
                # else:
                #     print('else++++++++++++++++++++++')
                #     product_data_ids = prod_templ_obj.search([('id', 'in', fetch_products)])

                product_data_ids = prod_templ_obj.search(
                    [('product_to_be_updated', '=', True)])

                for each in product_data_ids:
                    product = prestashop.get('products', each.presta_id)
                    categ = [{'id': each.categ_id.presta_id and str(each.categ_id.presta_id)}]
                    position_categ = each.categ_id.presta_id
                    if position_categ == False:
                        position_categ = 1
                    parent_id = each.categ_id.parent_id
                    while parent_id:
                        categ.append({'id': parent_id.presta_id and str(parent_id.presta_id)})
                        parent_id = parent_id.parent_id
                    # UPD categ
                    other_categories = self.get_categories(each)

                    for item in other_categories:
                        if item not in categ:
                            categ.append(item)

                    # if other_categories:
                    #     categ += other_categories

                    # union_sans_doublon = list({tuple(dictionnaire.items()) for dictionnaire in categ + other_categories})
                    # categ = [dict(element) for element in union_sans_doublon]

                    product.get('product').get('associations').update(
                        {'categories': {'attrs': {'nodeType': 'category', 'api': 'categories'}, 'category': categ}, })
                    name_by_languages = []
                    website_meta_description_by_languages = []
                    website_description_by_languages = []
                    website_meta_title_by_languages = []
                    seo_name_by_languages = []
                    website_meta_keywords_by_languages = []
                    description_short_by_languages = []
                    categ_sup = {}

                    for lang in self.env['prestashop.language'].search([]):
                        odoo_lang = self.env['res.lang'].search([('iso_code', '=', lang.code)])
                        video_url = each.video_url
                        if video_url:

                            insert_video = '<p><iframe width="560" height="315" src="' + video_url + '" frameborder="0"></iframe></p>'
                            insert_video = BeautifulSoup(insert_video, 'lxml')
                            insert_video = insert_video.body.next
                            print("======= insert vid ==========")
                            # print(a.body.next)
                            desc_with_video = str(insert_video) + str(
                                each.with_context(lang=odoo_lang.code).website_description)
                            print(desc_with_video)
                        else:
                            desc_with_video = each.with_context(lang=odoo_lang.code).website_description
                        website_description_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': desc_with_video}
                        )
                        name_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)}, 'value': each.with_context(lang=odoo_lang.code).name}
                        )
                        website_meta_title_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).website_meta_title}
                        )
                        website_meta_description_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).website_meta_description}
                        )
                        website_meta_keywords_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).website_meta_keywords}
                        )
                        seo_name_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).seo_name}
                        )
                        description_short_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).summary}
                        )
                        key = 'demande_catalogue_%s' % str(lang.presta_id)
                        key2 = 'sp_eacute_specifications_techniques_%s' % str(lang.presta_id)
                        categ_sup[key] = each.with_context(lang=odoo_lang.code).demande_catalogue if each.with_context(lang=odoo_lang.code).demande_catalogue else ""
                        categ_sup[key2] = each.with_context(lang=odoo_lang.code).sp_eacute_specifications_techniques

                        # 'demande_catalogue': data['associations']['dwf_extrafields']['dwf_extrafield'][
                        #     'demande_catalogue_%s' % self.lang_id.presta_id],
                        # 'sp_eacute_specifications_techniques':
                        # data['associations']['dwf_extrafields']['dwf_extrafield'][
                        #     'sp_eacute_specifications_techniques_%s' % self.lang_id.presta_id],
                    if each.image_1920 and len(each.product_img_ids) == 0:
                        self.fix_product_image(each)

                    image_vals = []
                    if each.product_img_ids:
                        for product_img in each.product_img_ids:
                            if product_img.prest_img_id:
                                if product_img.image_to_update:
                                    result_edit = self.edit_images(prestashop, product_img.file_db_store,
                                                                   each.presta_id, product_img.prest_img_id)
                                    logger.info("=======result_edit %s" % (result_edit))
                                    if ("Failed" in str(result_edit)) or ("200" not in str(result_edit)):
                                        logger.info("=======edit failed handle it here")
                                        presta_image_el = self.create_images(prestashop, product_img.file_db_store,
                                                                             each.presta_id, 'tushar.png')
                                        product_img.prest_img_id = int(presta_image_el['prestashop']['image']['id'])
                                        product_img.name = presta_image_el['prestashop']['image']['id']
                                        # image_vals.append({'id': str(product_img.prest_img_id)})

                                        if product_img.is_default_img and each.image_1920:
                                            each.prest_img_id = int(presta_image_el['prestashop']['image']['id'])
                                    # else:
                                    #     image_vals.append({'id': str(product_img.prest_img_id)})
                                    product_img.image_to_update = False
                            else:
                                presta_image_el = self.create_images(prestashop, product_img.file_db_store,
                                                                     each.presta_id, 'tushar.png')
                                product_img.prest_img_id = int(presta_image_el['prestashop']['image']['id'])
                                product_img.name = presta_image_el['prestashop']['image']['id']
                                # image_vals.append({'id': str(product_img.prest_img_id)})

                                if product_img.is_default_img and each.image_1920:
                                    each.prest_img_id = int(presta_image_el['prestashop']['image']['id'])

                            image_vals.append({'id': str(product_img.prest_img_id)})

                    id_default_image = {'attrs': {'notFilterable': 'true'}, 'value': ''}
                    if each.image_1920:
                        prest_img_id = each.prest_img_id
                        if prest_img_id == 0 and each.product_img_ids:
                            prest_img_id = each.product_img_ids.filtered(lambda l: l.is_default_img).prest_img_id
                            each.prest_img_id = prest_img_id
                        logger.info("=======prest_img_id  after %s" % (prest_img_id))
                        id_default_image = {'attrs': {'notFilterable': 'true'}, 'value': str((prest_img_id))}

                    old_img_ids = product.get('product').get('associations').get('images').get('image',
                                                                                               False) if product.get(
                        'product').get('associations', False) and product.get('product').get('associations').get(
                        'images', False) else []
                    img_to_delete = []
                    if old_img_ids:
                        if not isinstance(old_img_ids, list):
                            old_img_ids = [old_img_ids]
                        if len(image_vals) == 0:
                            img_to_delete = [img["id"] for img in old_img_ids]
                        elif len(image_vals) > 0:
                            for img in old_img_ids:
                                if img not in image_vals:
                                    img_to_delete.append(img["id"])
                    img_to_delete = list(set(img_to_delete)) if len(img_to_delete) > 0 else img_to_delete
                    logger.info("=======> old_img_ids presta %s" % old_img_ids)
                    logger.info("=======> img_to_delete presta %s" % img_to_delete)

                    product_update_vals = {

                        # 'name': {'language': {'attrs': {'id': '1'}, 'value': each.name and str(each.name)}},
                        'name': {'language': name_by_languages},
                        'associations': {
                            'dwf_extrafields': {
                                'dwf_extrafields': categ_sup
                            },
                            'images': {'attrs': {'nodeType': 'image', 'api': 'images'},
                                        'image': image_vals},
                            'categories': {'attrs': {'nodeType': 'category', 'api': 'categories'}, 'category': categ}
                        },
                        'active': each.website_published and '1' or '0',
                        'type': 'simple',
                        'on_sale': each.product_onsale and '1' or '0',
                        'state': '1',
                        'online_only': '1',
                        'reference': each.default_code and str(each.default_code),
                        'wholesale_price': each.wholesale_price and str(each.wholesale_price),
                        'price': each.list_price and str(each.list_price),
                        'depth': each.product_lngth and str(each.product_lngth),
                        'width': each.product_width and str(each.product_width),
                        'weight': each.product_wght and str(each.product_wght),
                        'height': each.product_hght and str(each.product_hght),
                        'description': {'language': website_description_by_languages},
                        # 'description': '<p><iframe width="560" height="315" src="https://www.youtube.com/embed/Fpf81wjAgxQ?rel=0" frameborder="0"></iframe></p>',
                        'available_now': ({'language': {'attrs': {'id': '1'}, 'value': each.product_instock and str(
                            int(each.product_instock))}}),
                        # 'on_sale': each.product_onsale and str(int(each.product_onsale)),
                        'id': each.presta_id and str(each.presta_id),
                        'id_category_default': each.categ_id and str(each.categ_id.presta_id),
                        'meta_title': {'language': website_meta_title_by_languages},
                        'meta_description': {'language': website_meta_description_by_languages},
                        'meta_keywords': {'language': website_meta_keywords_by_languages},
                        'link_rewrite': {'language': seo_name_by_languages},
                        'description_short': {'language': description_short_by_languages},
                        'position_in_category': '1',
                        'condition': each.condition,
                        'id_default_image': id_default_image,
                        # 'description': {'language': {'attrs': {'id': '1'}, 'value': each.product_description}}
                        # 'name': {'language': {'attrs': {'id': '1'}, 'value': each.prd_label}},
                        # 'product_img_ids':product.get('associations').get('images').get('image') or False,
                    }

                    if each.supplier_id:
                        product_update_vals.update({
                            'id_supplier': each.supplier_id and str(each.supplier_id.presta_id) or '0',
                        })

                    if each.manufacturer_id:
                        product_update_vals.update({
                            'id_manufacturer': each.manufacturer_id and str(each.manufacturer_id.presta_id) or '0',
                        })

                    product.get('product').update(product_update_vals)

                    if each.product_spec_ids:
                        features_data = product.get('product').get('associations').get(
                            'product_features').get('product_feature')
                        feature_values = []
                        for feature_id in each.product_spec_ids:
                            vals = {
                                'id': str(feature_id.feature.presta_id),
                                'id_feature_value': str(feature_id.feature_value.presta_id)
                            }
                            feature_values.append(vals)

                        product.get('product').get('associations').get('product_features').update(
                            {'product_feature': feature_values})

                    product.get('product').pop('quantity')
                    combination_list = []
                    if each.attribute_line_ids:
                        prod_variant_ids = prdct_obj.search([('product_tmpl_id', '=', each.id)])
                        for variant in prod_variant_ids:
                            if variant.combination_id:
                                prod_variants_comb = prestashop.get('combinations', variant.combination_id)
                                option_values = []
                                # for op in variant.product_template_attribute_value_ids:
                                #     option_values.append({'id': op.presta_id and str(op.presta_id)})
                                # prod_variants_comb.get('combination').get('associations').get(
                                #     'product_option_values').update({
                                #     'product_option_value': option_values[0]
                                # })
                                #
                                prod_variants_comb.get('combination').update({
                                    'is_virtual': '1',
                                    'id_product': variant.product_tmpl_id and str(
                                        variant.product_tmpl_id.presta_id),
                                    'reference': variant.default_code and str(variant.default_code),
                                    'id': variant.combination_id and str(variant.combination_id),
                                    'minimal_quantity': '1',
                                    'price': variant.prdct_unit_price and str(variant.prdct_unit_price),
                                })
                                response_comb = prestashop.edit('combinations', prod_variants_comb)
                                combination_list.append({'id': variant.combination_id})
                    if combination_list:
                        product.get('product').get('associations').get('combinations').update({
                            'combination': combination_list
                        })
                    product.get('product').pop('manufacturer_name')
                    print('\nproduct updated++++++++++++++++++++', product)
                    shop.write({'prestashop_last_update_product_data_date': datetime.now()})
                    response = prestashop.edit('products', product)
                    if len(img_to_delete) > 0:
                        delete_response = self.delete_images(each.presta_id, img_to_delete)
                    logger.info("=======> response %s " % response)
                    each.write({
                        'product_to_be_updated': False
                    })
                shop.write({'prestashop_last_update_product_data_date': datetime.now()})
                shop.env.cr.commit()
            # except Exception as e:
            #     shop.write({'prestashop_last_update_product_data_date': datetime.now()})
            #     print('Date Updated')
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'update_product_data',
            #              'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context

        return True

    def fix_product_image(self, product_id):
        product_image_obj = self.env['gt.prestashop.product.images']
        for shop in self:
            logger.info("=======> Track fix_product_imgae")
            if product_id:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                if prestashop:
                    product = prestashop.get('products', product_id.presta_id)
                    if product:
                        id_default_image = product.get('product').get('id_default_image').get('value', False)
                        logger.info("=======> id_default_image %s" % id_default_image)
                        logger.info("=======> product %s " % (product))

                        img_ids = product.get('product').get('associations').get('images').get('image', False) if product.get('product').get('associations', False) and product.get('product').get('associations').get('images', False) else []
                        logger.info("=======> img_ids presta %s" % img_ids)
                        if img_ids:
                            logger.info("=======> img_ids %s " % img_ids)
                            logger.info("=======> product_img_ids %s " % product_id.product_img_ids)
                            if not isinstance(img_ids, list):
                                img_ids = [img_ids]

                            image_list = []
                            for image in img_ids:
                                logger.info("=======> image %s " % image)
                                if image.get('id') != '0':
                                    logger.info("=======> lets go set value for prestImgId ")
                                    loc = (self.prestashop_instance_id.location).split('//')
                                    url = "http://" + self.prestashop_instance_id.webservice_key + "@" + loc[
                                        1] + '/api/images/products/' + product.get('product').get('id') + '/' + image.get('id')
                                    client = PrestaShopWebServiceImage(self.prestashop_instance_id.location,
                                                                       self.prestashop_instance_id.webservice_key)
                                    res = client.get_image(url)
                                    if res.get('image_content'):
                                        logger.info("=======> res.get('image_content') we find the image on presta" )
                                        img_test = res.get('image_content').decode('utf-8')
                                        extention = res.get('type')
                                        if img_test and product_id.image_1920 == img_test:
                                            logger.info("=======> default images are sames")
                                            product_id.prest_img_id = int(image.get('id'))
                                        # fill list img
                                        if img_test:
                                            product_img_id = product_image_obj.search(
                                                [('prest_img_id', '=', int(image.get('id'))),
                                                 ('product_t_id', '=', product_id.id)])
                                            logger.info("=======> product_img_id %s " % product_img_id)
                                            if not product_img_id:
                                                is_default_img = False
                                                if (id_default_image and (id_default_image != '' or id_default_image is not None) and int(image.get('id')) == int(id_default_image)):
                                                    is_default_img = True
                                                    val_toUpd = {
                                                        'prest_img_id': int(id_default_image),
                                                    }
                                                    if product_id.image_1920 and product_id.image_1920 != img_test:
                                                        val_toUpd['image_1920'] = img_test
                                                    product_id.with_context(skip_write_control=True).update(val_toUpd)

                                                img_vals = {'is_default_img': is_default_img,
                                                     'extention': extention,
                                                     'image_url': url,
                                                     'image': img_test,
                                                     'file_db_store': img_test,
                                                     'prest_product_id': product_id.presta_id,
                                                     'prest_img_id': int(image.get('id')),
                                                     'name': image.get('id'),
                                                     'product_t_id': product_id.id}
                                                logger.info("=======> product_image_ids  vals %s " % img_vals)
                                                product_image_obj.create(img_vals)
                                            else:
                                                if (id_default_image and (id_default_image != '' or id_default_image is not None) and int(image.get('id')) == int(id_default_image)):
                                                    val_toUpd = {
                                                        'prest_img_id': int(id_default_image),
                                                    }
                                                    if product_id.image_1920 and product_id.image_1920 != img_test:
                                                        val_toUpd['image_1920'] = img_test
                                                    product_id.with_context(skip_write_control=True).update(val_toUpd)

    def edit_images(self, prestashop, image_data, product_id, prest_img_id, image_name=None):
        logger.info("=======edit_images")
        image = {
                'content': image_data,
            }
        resource = 'images/products/' + str(product_id) + '/' + str(prest_img_id)
        logger.info("=======url %s " % resource)
        try:
            # result = prestashop.edit(resource, image)
            url = self.prestashop_instance_id.location
            key = self.prestashop_instance_id.webservice_key
            result = requests.put(url + '/api/images/products/%s/%s' % (str(product_id), str(prest_img_id)), auth=(key, ''), data=image)

        except Exception as e:
            result = "Failed to edit image " + str(e)
        logger.info("=======result %s" % (result))
        return result

    def delete_images(self, product_id, prest_img_ids):
        logger.info("=======delete_images")
        try:
            url = self.prestashop_instance_id.location
            key = self.prestashop_instance_id.webservice_key
            result = ""
            for imgId in prest_img_ids:
                r = requests.delete(url + '/api/images/products/%s/%s' % (str(product_id), str(imgId)), auth=(key, ''))
                result += str(r) + " - "
        except Exception as e:
            result = "Failed to delete image" + str(e)
        logger.info("=======result %s" % (result))
        return result

    def get_parent_category(self, categ):
        """Recursive function for parent category"""
        if categ and categ.presta_id:
            return {str(categ.presta_id)} | self.get_parent_category(categ.parent_id)
        else:
            return set()

    def get_categories(self, product):
        """Getting categories from product in presta format
           ex. [{'id': 1},{'id':2}]"""
        categories = product.product_category_ids.filtered(lambda x: x.presta_id)
        logger.info("=======> product_category_ids %s" % product.product_category_ids)
        logger.info("=======> categories with presta_id %s" % product.product_category_ids)
        all_categ = set()
        for categ in categories:
            if categ.presta_id:
                all_categ |= {str(categ.presta_id)} | self.get_parent_category(categ.parent_id)
        return [{'id': x} for x in all_categ]

    def update_one_product(self, variant=False, product_id=False):
        # update product details,image and variants
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        category_obj = self.env['product.category']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            query = "select product_id from product_templ_shop_rel_ where shop_id = %s" % shop.id
            self.env.cr.execute(query)
            fetch_products = self.env.cr.fetchall()
            if fetch_products is not None:
                fetch_products = [i[0] for i in fetch_products]
                # if shop.prestashop_last_update_product_data_date:
                #     print('if+++++++++++++++', shop.prestashop_last_update_product_data_date)
                #
                #     product_data_ids = prod_templ_obj.search(
                #         [('write_date', '>', shop.prestashop_last_update_product_data_date),
                #          ])
                #     # ('id', 'in', fetch_products)])
                # else:
                #     print('else++++++++++++++++++++++')
                #     product_data_ids = prod_templ_obj.search([('id', 'in', fetch_products)])

                product_data_ids = prod_templ_obj.search(
                    [
                        ('product_to_be_updated', '=', True),
                        ('id', '=', product_id)
                    ])

                for each in product_data_ids:
                    product = prestashop.get('products', each.presta_id)
                    logger.info("=========produc=== %s " % (product))
                    categ = [{'id': each.categ_id.presta_id and str(each.categ_id.presta_id)}]
                    position_categ = each.categ_id.presta_id
                    if position_categ == False:
                        position_categ = 1
                    parent_id = each.categ_id.parent_id
                    while parent_id:
                        categ.append({'id': parent_id.presta_id and str(parent_id.presta_id)})
                        parent_id = parent_id.parent_id
                    # UPD categ
                    logger.info("=========Before categ=== %s " % (categ))
                    other_categories = self.get_categories(each)
                    # if other_categories:
                    #     categ += other_categories

                    for item in other_categories:
                        if item not in categ:
                            categ.append(item)

                    logger.info("=========other_categories=== %s " % (other_categories))
                    logger.info("=========categ=== %s " % (categ))

                    product.get('product').get('associations').update(
                        {'categories': {'attrs': {'nodeType': 'category', 'api': 'categories'}, 'category': categ}, })
                    name_by_languages = []
                    website_meta_description_by_languages = []
                    website_description_by_languages = []
                    website_meta_title_by_languages = []
                    seo_name_by_languages = []
                    website_meta_keywords_by_languages = []
                    description_short_by_languages = []
                    categ_sup = {}

                    for lang in self.env['prestashop.language'].search([]):
                        odoo_lang = self.env['res.lang'].search([('iso_code', '=', lang.code)])
                        video_url = each.video_url
                        if video_url:

                            insert_video = '<p><iframe width="560" height="315" src="' + video_url + '" frameborder="0"></iframe></p>'
                            insert_video = BeautifulSoup(insert_video, 'lxml')
                            insert_video = insert_video.body.next
                            # print(a.body.next)
                            desc_with_video = str(insert_video) + str(
                                each.with_context(lang=odoo_lang.code).website_description)
                        else:
                            desc_with_video = each.with_context(lang=odoo_lang.code).website_description
                        website_description_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': desc_with_video}
                        )
                        name_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)}, 'value': each.with_context(lang=odoo_lang.code).name}
                        )
                        website_meta_title_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).website_meta_title}
                        )
                        website_meta_description_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).website_meta_description}
                        )
                        website_meta_keywords_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).website_meta_keywords}
                        )
                        seo_name_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).seo_name}
                        )
                        description_short_by_languages.append(
                            {'attrs': {'id': str(lang.presta_id)},
                             'value': each.with_context(lang=odoo_lang.code).summary}
                        )
                        key = 'demande_catalogue_%s' % str(lang.presta_id)
                        key2 = 'sp_eacute_specifications_techniques_%s' % str(lang.presta_id)
                        categ_sup[key] = each.with_context(lang=odoo_lang.code).demande_catalogue if each.with_context(lang=odoo_lang.code).demande_catalogue else ""
                        categ_sup[key2] = each.with_context(lang=odoo_lang.code).sp_eacute_specifications_techniques

                        # 'demande_catalogue': data['associations']['dwf_extrafields']['dwf_extrafield'][
                        #     'demande_catalogue_%s' % self.lang_id.presta_id],
                        # 'sp_eacute_specifications_techniques':
                        # data['associations']['dwf_extrafields']['dwf_extrafield'][
                        #     'sp_eacute_specifications_techniques_%s' % self.lang_id.presta_id],
                    if each.image_1920 and len(each.product_img_ids) == 0:
                        self.fix_product_image(each)

                    image_vals = []
                    if each.product_img_ids:
                        for product_img in each.product_img_ids:
                            if product_img.prest_img_id:
                                if product_img.image_to_update:
                                    result_edit = self.edit_images(prestashop, product_img.file_db_store, each.presta_id, product_img.prest_img_id)
                                    if ("Failed" in str(result_edit)) or ("200" not in str(result_edit)):
                                        presta_image_el = self.create_images(prestashop, product_img.file_db_store,
                                                                             each.presta_id, 'tushar.png')
                                        product_img.prest_img_id = int(presta_image_el['prestashop']['image']['id'])
                                        product_img.name = presta_image_el['prestashop']['image']['id']
                                        # image_vals.append({'id': str(product_img.prest_img_id)})

                                        if product_img.is_default_img and each.image_1920:
                                            each.prest_img_id = int(presta_image_el['prestashop']['image']['id'])
                                    # else:
                                    #     image_vals.append({'id': str(product_img.prest_img_id)})
                                    product_img.image_to_update = False
                            else:
                                presta_image_el = self.create_images(prestashop, product_img.file_db_store, each.presta_id,'tushar.png')
                                product_img.prest_img_id = int(presta_image_el['prestashop']['image']['id'])
                                product_img.name = presta_image_el['prestashop']['image']['id']
                                # image_vals.append({'id': str(product_img.prest_img_id)})

                                if product_img.is_default_img and each.image_1920:
                                    each.prest_img_id = int(presta_image_el['prestashop']['image']['id'])

                            image_vals.append({'id': str(product_img.prest_img_id)})

                    id_default_image = {'attrs': {'notFilterable': 'true'}, 'value': ''}
                    if each.image_1920:
                        prest_img_id = each.prest_img_id
                        if prest_img_id == 0 and each.product_img_ids:
                            prest_img_id = each.product_img_ids.filtered(lambda l: l.is_default_img).prest_img_id
                            each.prest_img_id = prest_img_id
                        id_default_image = {'attrs': {'notFilterable': 'true'}, 'value': str((prest_img_id))}


                    old_img_ids = product.get('product').get('associations').get('images').get('image',
                                                                                           False) if product.get(
                        'product').get('associations', False) and product.get('product').get('associations').get(
                        'images', False) else []
                    img_to_delete = []
                    if old_img_ids:
                        if not isinstance(old_img_ids, list):
                            old_img_ids = [old_img_ids]
                        if len(image_vals) == 0:
                            img_to_delete = [img["id"] for img in old_img_ids]
                        elif len(image_vals) > 0:
                            for img in old_img_ids:
                                if img not in image_vals:
                                    img_to_delete.append(img["id"])
                    img_to_delete = list(set(img_to_delete)) if len(img_to_delete) > 0 else img_to_delete

                    product_update_vals = {

                        # 'name': {'language': {'attrs': {'id': '1'}, 'value': each.name and str(each.name)}},
                        'name': {'language': name_by_languages},
                        'associations': {
                            'dwf_extrafields': {
                                'dwf_extrafields': categ_sup
                            },
                            'images': {'attrs': {'nodeType': 'image', 'api': 'images'},
                                        'image': image_vals},
                            'categories': {'attrs': {'nodeType': 'category', 'api': 'categories'}, 'category': categ}
                        },
                        'active': each.website_published and '1' or '0',
                        'type': 'simple',
                        'on_sale': each.product_onsale and '1' or '0',
                        'state': '1',
                        'online_only': '1',
                        'reference': each.default_code and str(each.default_code),
                        'wholesale_price': each.wholesale_price and str(each.wholesale_price),
                        'price': each.list_price and str(each.list_price),
                        'depth': each.product_lngth and str(each.product_lngth),
                        'width': each.product_width and str(each.product_width),
                        'weight': each.product_wght and str(each.product_wght),
                        'height': each.product_hght and str(each.product_hght),
                        'description': {'language': website_description_by_languages},
                        # 'description': '<p><iframe width="560" height="315" src="https://www.youtube.com/embed/Fpf81wjAgxQ?rel=0" frameborder="0"></iframe></p>',
                        'available_now': ({'language': {'attrs': {'id': '1'}, 'value': each.product_instock and str(
                            int(each.product_instock))}}),
                        # 'on_sale': each.product_onsale and str(int(each.product_onsale)),
                        'id': each.presta_id and str(each.presta_id),
                        'id_category_default': each.categ_id and str(each.categ_id.presta_id),
                        'meta_title': {'language': website_meta_title_by_languages},
                        'meta_description': {'language': website_meta_description_by_languages},
                        'meta_keywords': {'language': website_meta_keywords_by_languages},
                        'link_rewrite': {'language': seo_name_by_languages},
                        'description_short': {'language': description_short_by_languages},
                        'position_in_category': 1,
                        'condition': each.condition,
                        'id_default_image': id_default_image,
                        # 'description': {'language': {'attrs': {'id': '1'}, 'value': each.product_description}}
                        # 'name': {'language': {'attrs': {'id': '1'}, 'value': each.prd_label}},
                        # 'product_img_ids':product.get('associations').get('images').get('image') or False,
                    }

                    if each.supplier_id:
                        product_update_vals.update({
                            'id_supplier': each.supplier_id and str(each.supplier_id.presta_id) or '0',
                        })

                    if each.manufacturer_id:
                        product_update_vals.update({
                            'id_manufacturer': each.manufacturer_id and str(each.manufacturer_id.presta_id) or '0',
                        })

                    product.get('product').update(product_update_vals)

                    if each.product_spec_ids:
                        features_data = product.get('product').get('associations').get(
                            'product_features').get('product_feature')
                        feature_values = []
                        for feature_id in each.product_spec_ids:
                            vals = {
                                'id': str(feature_id.feature.presta_id),
                                'id_feature_value': str(feature_id.feature_value.presta_id)
                            }
                            feature_values.append(vals)

                        product.get('product').get('associations').get('product_features').update(
                            {'product_feature': feature_values})

                    product.get('product').pop('quantity')
                    combination_list = []
                    if each.attribute_line_ids:
                        prod_variant_ids = prdct_obj.search([('product_tmpl_id', '=', each.id)])
                        for variant in prod_variant_ids:
                            if variant.combination_id:
                                prod_variants_comb = prestashop.get('combinations', variant.combination_id)
                                option_values = []
                                # for op in variant.product_template_attribute_value_ids:
                                #     option_values.append({'id': op.presta_id and str(op.presta_id)})
                                # prod_variants_comb.get('combination').get('associations').get(
                                #     'product_option_values').update({
                                #     'product_option_value': option_values[0]
                                # })
                                #
                                prod_variants_comb.get('combination').update({
                                    'is_virtual': '1',
                                    'id_product': variant.product_tmpl_id and str(
                                        variant.product_tmpl_id.presta_id),
                                    'reference': variant.default_code and str(variant.default_code),
                                    'id': variant.combination_id and str(variant.combination_id),
                                    'minimal_quantity': '1',
                                    'price': variant.prdct_unit_price and str(variant.prdct_unit_price),
                                })
                                response_comb = prestashop.edit('combinations', prod_variants_comb)
                                combination_list.append({'id': variant.combination_id})
                    if combination_list:
                        product.get('product').get('associations').get('combinations').update({
                            'combination': combination_list
                        })
                    product.get('product').pop('manufacturer_name')
                    shop.write({'prestashop_last_update_product_data_date': datetime.now()})
                    logger.info("=======> product %s " % product)
                    logger.info("=======> product_update_vals filled %s " % product_update_vals)
                    response = prestashop.edit('products', product)
                    if len(img_to_delete) > 0:
                        delete_response = self.delete_images(each.presta_id, img_to_delete)
                    logger.info("=======> response %s " % response)
                    each.write({
                        'product_to_be_updated': False
                    })
                shop.write({'prestashop_last_update_product_data_date': datetime.now()})
                shop.env.cr.commit()
            # except Exception as e:
            #     shop.write({'prestashop_last_update_product_data_date': datetime.now()})
            #     print('Date Updated')
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'update_product_data',
            #              'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context

        return True

    # def update_products_feature(self, variant=False):
    #     prod_templ_obj = self.env['product.template']
    #     prdct_obj = self.env['product.product']
    #     for shop in self:
    #         prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
    #                                               shop.prestashop_instance_id.webservice_key or None)
    #
    #         query = "select product_id from product_templ_shop_rel where shop_id = %s" % shop.id
    #         self.env.cr.execute(query)
    #         fetch_products = self.env.cr.fetchall()
    #         if fetch_products is not None:
    #             fetch_products = [i[0] for i in fetch_products]
    #             # if shop.prestashop_last_update_product_data_date:
    #             #     product_data_ids = prod_templ_obj.search(
    #             #         [('write_date', '>=', shop.prestashop_last_update_product_data_date),
    #             #          ('id', 'in', fetch_products)])
    #             # else:
    #             product_data_ids = prod_templ_obj.search([('id', 'in', fetch_products)])
    #
    #             for each in product_data_ids:
    #                 print('each.presta_id+++++++', each.presta_id)
    #
    #                 filters = {'display': 'full', 'filter[id]': str(each.presta_id)}
    #                 product_data = prestashop.get('products', options=filters)
    #                 print("\n<><><><><><><>product_data>>>>>>>>>>>", product_data)
    #
    #                 features_list = []
    #                 features_data = product_data.get('products').get('product').get('associations').get(
    #                     'product_features').get('product_feature')
    #                 print("\n<><><><><><><>features_data>>>>>>>>>>>", features_data)
    #
    #                 for product_features_id in features_data:
    #                     print("\n<><><><><><<>>>>product_features_id>>>>>>old>>>>>>", product_features_id)
    #
    #                     product_features_id['id'] = '1'
    #                     product_features_id['id_feature_value'] = '2'
    #                     # vals = {
    #                     #     'id': 1,
    #                     #     'id_feature_value': 2
    #                     # }
    #                     print("<><><><><><<>>>>product_features_id>>>>>>new>>>>>>", product_features_id)
    #
    #                     features_list.append(product_features_id)
    #                     # features_list.append(vals)
    #                     print("\n<><><><><><<>>>>features_list>>>>>>>>>>>>", features_list)
    #
    #                     # product_data.get('products').update({
    #                     #     'id': each.presta_id,
    #                     #     'price': each.list_price,
    #                     # })
    #                     print('product_data+++++++++++++++++', product_data)
    #
    #                     product_data.get('products').get('product').get('associations').get('product_features').update(
    #                         {'product_feature': features_list})
    #
    #                     # product_features_id['features_data'].update({'id': '1', 'id_feature_value': '2'})
    #                     features_update = prestashop.edit('products', product_data)

    # 	@api.multi
    # 	def update_product_price(self):
    # 		print ("======update_product_price======")
    # 		# update product price
    # 		prod_templ_obj = self.env['product.template']
    # 		prdct_obj = self.env['product.product']
    # 		stock_quant_obj = self.env['stock.quant']
    #
    # 		for shop in self:
    # 			prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,
    # 												  shop.prestashop_instance_id.webservice_key,physical_url = shop.shop_physical_url or None)
    # #             try:
    # 			query = "select product_id from product_templ_shop_rel where shop_id = %s"%shop.id
    # 			self.env.cr.execute(query)
    # 			fetch_products_price = self.env.cr.fetchall()
    # 			if fetch_products_price != None:
    # 				fetch_products_price = [i[0] for i in fetch_products_price]
    # 				# if shop.prestashop_last_update_product_data_date:
    # 				#     product_data_ids = prod_templ_obj.search(
    # 				#         [('write_date', '>=', shop.prestashop_last_update_product_data_date),('id', 'in',fetch_products_price)])
    # 				#     print ("=====product_data_ids111111======",product_data_ids)
    # 				# else:
    # 				product_data_ids = prod_templ_obj.search([('id', 'in',fetch_products_price)])
    # 				for each in product_data_ids:
    # 							# print ("EACHHHHHHHHH",each)
    # #                             try:
    # 							product = prestashop.get('products', each.presta_id)
    # 							# print ("PRODUCTTTTTTTTTT",product)
    # 							categ = [{'id': each.presta_categ_id.presta_id}]
    # 							parent_id = each.presta_categ_id.parent_id
    # 							while parent_id:
    # 								categ.append({'id': parent_id.presta_id})
    # 								parent_id = parent_id.parent_id
    # 							product.get('product').get('associations').update({
    # 								'categories': {'attrs': {'node_type': 'category'}, 'category': categ},
    # 							})
    #
    # 							product.get('product').update({
    # 								# 'price': str(each.prdct_unit_price),
    # 								'price': str(each.with_context(pricelist=self.pricelist_id.id).price),
    # #                                 'quantity':0,
    # 								'wholesale_price': each.wholesale_price and str(each.wholesale_price),
    # 								'id': each.presta_id and str(each.presta_id),
    # 								'position_in_category':'',
    # 								'id_category_default':each.presta_categ_id and str(each.presta_categ_id) and each.presta_categ_id.presta_id,
    # 								# 'available_now': (
    # 								# {'language': {'attrs': {'id': '1'}, 'value': str(int(each.product_instock))}}),
    # 								# 'on_sale': str(int(each.product_onsale)),
    # 								# 'id': each.presta_id,
    # 							})
    #
    # 							if each.attribute_line_ids:
    # 								# try:
    # 								prod_variant_ids = prdct_obj.search([('product_tmpl_id', '=', each.id)])
    # 									# if not prod_variant_ids:
    #
    # 								for variant in prod_variant_ids:
    # 										if variant.combination_id:
    # 											print("=======prod_variant_ids========>",prod_variant_ids)
    # 											print("=======prestashop.get('combinations'========>",prestashop.get('combinations'))
    # 											prod_variants_comb = prestashop.get('combinations', variant.combination_id)
    # 											print("=======prod_variants_comb========>",prod_variants_comb)
    # 											# prod_variants_comb_price = prestashop.get('combinations', variant.combination_price)
    # 											# print "prod_variants_comb_price===>",prod_variants_comb_price
    # #                                             option_values = []
    # #                                             for op in variant.attribute_value_ids:
    # #                                                 option_values.append({'id': op.presta_id})
    # #                                             prod_variants_comb.get('combination').get('associations').get('product_option_values').update({
    # #                                                 'product_option_value' : option_values
    # #                                             })
    # 											prod_variants_comb.get('combination').update({
    # 												# 'id_product': variant.product_tmpl_id.presta_id,
    # 												# 'reference': variant.default_code,
    # 												'minimal_quantity': '1',
    # #                                                 'position_in_category':'',
    # 												# 'price': str(variant.prdct_unit_price),
    # 												# 'id': variant.combination_id and str(variant.combination_id),
    # 												# 'id_product': variant.product_tmpl_id and str(variant.product_tmpl_id.presta_id),
    # 												'id_product': variant.product_tmpl_id and variant.product_tmpl_id.presta_id and str(variant.product_tmpl_id.presta_id),
    # 												'price': str(variant.with_context(pricelist=self.pricelist_id.id).price),
    # 												'wholesale_price': variant.wholesale_price and str(variant.wholesale_price),
    # 											})
    # 											prod_variants_comb.get('combination').pop('quantity')
    # 											# print("==========result=======>",result)
    # 											prestashop.edit('combinations', prod_variants_comb)
    # 								# except:
    # 								#     pass
    # #
    # 							product.get('product').pop('manufacturer_name')
    # 							product.get('product').pop('quantity')
    # 							prestashop.edit('products', product)
    # #                             except Exception as e:
    # #                                 if self.env.context.get('log_id'):
    # #                                     log_id = self.env.context.get('log_id')
    # #                                     self.env['log.error'].create(
    # #                                         {'log_description': str(e) + ' While updating product price %s' % (each.name),
    # #                                          'log_id': log_id})
    # #                                 else:
    # #                                     log_id = self.env['prestashop.log'].create({'all_operations': 'update_product_price',
    # #                                                                                 'error_lines': [(0, 0, {'log_description': str(
    # #                                                                                     e) + ' While updating product price %s' % (
    # #                                                                                 each.name)})]})
    # #                                     self = self.with_context(log_id=log_id.id)
    #
    # #             except Exception as e:
    # #                 if self.env.context.get('log_id'):
    # #                     log_id = self.env.context.get('log_id')
    # #                     self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
    # #                 else:
    # #                     log_id = self.env['prestashop.log'].create(
    # #                         {'all_operations': 'update_product_price', 'error_lines': [(0, 0, {'log_description': str(e)})]})
    # #                     self = self.with_context(log_id=log_id.id)
    # 		shop.write({'prestashop_last_update_product_data_date': datetime.now()})
    # 		return True

    def update_quantity_prestashop(self, prestashop, pid, quantity, shop_id, attribute_id=None):
        option = {'id_shop': shop_id, 'filter[id_product]': pid}
        if attribute_id is not None:
            option.update({'filter[id_product_attribute]': attribute_id})
        # try:
        stock_search = prestashop.get('stock_availables', options=option)
        print('\nstock_search+++++++++++++++++', stock_search)
        if type(stock_search.get('stock_availables')) == dict:
            prestashop_qty_pack_list = stock_search['stock_availables']['stock_available']
            prestashop_qty_pack_list = self.action_check_isinstance(prestashop_qty_pack_list)
            print('prestashop_qty_pack_list++++++++++', prestashop_qty_pack_list)
            for stock in prestashop_qty_pack_list:
                stock_id = stock.get('attrs').get('id')
                # stock_id = stock_search['stock_availables']['stock_available']['attrs']['id']
                try:
                    stock_data = prestashop.get('stock_availables', stock_id)
                except Exception as e:
                    return [0, ' Error in Updating Quantity,can`t get stock_available data.']
                if type(quantity) == str:
                    quantity = quantity.split('.')[0]
                if type(quantity) == float:
                    quantity = int(quantity)
                stock_data['stock_available']['quantity'] = int(quantity)
                stock_data.get('stock_available').update({'quantity': str(quantity), })
                try:
                    prestashop.edit('stock_availables', stock_data)
                except Exception as e:
                    pass
        else:
            pass

    # def update_quantity_prestashop(self, prestashop, pid, quantity, shop_id, attribute_id=None):
    #     option = {'id_shop': shop_id, 'filter[id_product]': pid}
    #     if attribute_id is not None:
    #         option.update({'filter[id_product_attribute]': attribute_id})
    #     # try:
    #     stock_search = prestashop.get('stock_availables', options=option)
    #     if type(stock_search.get('stock_availables')) == dict:
    #         print('stock_search+++++++++', stock_search['stock_availables']['stock_available'])
    #         stock_id = stock_search['stock_availables']['stock_available']['attrs']['id']
    #         try:
    #             stock_data = prestashop.get('stock_availables', stock_id)
    #         except Exception as e:
    #             return [0, ' Error in Updating Quantity,can`t get stock_available data.']
    #         if type(quantity) == str:
    #             quantity = quantity.split('.')[0]
    #         if type(quantity) == float:
    #             quantity = int(quantity)
    #         stock_data['stock_available']['quantity'] = int(quantity)
    #         stock_data.get('stock_available').update({'quantity': str(quantity), })
    #         try:
    #             prestashop.edit('stock_availables', stock_data)
    #         except Exception as e:
    #             pass
    #     else:
    #         pass

    # except Exception as e:
    # 	pass

    # @api.multi
    def update_presta_product_inventory(self):
        prodct_templ_obj = self.env['product.template']
        prodct_obj = self.env['product.product']
        stock_quant_obj = self.env['stock.quant']
        try:
            for shop in self:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                self.env.cr.execute("update product_template set prestashop_update_stock= False;")
                product_tmpl_ids = prodct_templ_obj.search([('prestashop_update_stock', '=', False)])
                if product_tmpl_ids:
                    for product_tmpl_id in product_tmpl_ids:
                        if product_tmpl_id.presta_id:
                            product_product_ids = prodct_obj.search([('product_tmpl_id', '=', product_tmpl_id.id)])
                            if product_tmpl_id.presta_id:
                                if len(product_product_ids) == 1:
                                    stock_quant_ids = stock_quant_obj.search(
                                        [('location_id', '=', shop.warehouse_id.lot_stock_id.id),
                                         ('product_id', '=', product_product_ids.id)])
                                    quantity_avilable = sum(
                                        stock_quant_id.quantity for stock_quant_id in stock_quant_ids)
                                    shop.update_quantity_prestashop(prestashop, product_tmpl_id.presta_id,
                                                                    quantity_avilable, shop.presta_id)

                                else:
                                    for product_product_id in product_product_ids:
                                        if product_product_id.combination_id:
                                            stock_quant_ids = stock_quant_obj.search(
                                                [('location_id', '=', shop.warehouse_id.lot_stock_id.id),
                                                 ('product_id', '=', product_product_id.id)])
                                            quantity_avilable = sum(
                                                stock_quant_id.quantity for stock_quant_id in stock_quant_ids)
                                            combination_id = product_product_id.combination_id
                                            shop.update_quantity_prestashop(prestashop, product_tmpl_id.presta_id,
                                                                            quantity_avilable, shop.presta_id,
                                                                            combination_id)
                            product_tmpl_id.write({'prestashop_update_stock': True})

        except Exception as e:
            if self.env.context.get('log_id'):
                log_id = self.env.context.get('log_id')
                self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            else:
                log_id_obj = self.env['prestashop.log'].create(
                    {'all_operations': 'update_inventory', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                log_id = log_id_obj.id
            new_context = dict(self.env.context)
            new_context.update({'log_id': log_id})
            self.env.context = new_context

    # @api.multi
    def update_order_status(self):
        sale_order = self.env['sale.order']
        status_obj = self.env['presta.order.status']
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            sale_order_ids = sale_order.search([('order_status_update', '=', True)])
            print("sale_order_ids_++++++++++++++=", sale_order_ids)
            try:
                for sale_order_id in sale_order_ids:
                    order_his_data = prestashop.get('order_histories', options={'schema': 'blank'})
                    order_his_data['order_history'].update({
                        'id_order': str(sale_order_id.presta_id),
                        'id_order_state': str(sale_order_id.order_status.presta_id)
                    })
                    state_update = prestashop.add('order_histories', order_his_data)
                    shop.env.cr.commit()
            except Exception as e:
                print('Except++++++++++++++++++++', e)

    def create_images(self, prestashop, image_data, resource_id, image_name=None, resource='images/products'):
        if image_name == None:
            image_name = 'op' + str(resource_id) + '.png'
        # try:
        # print(",.,.,.,.,.,..,,..,.,ALLLLLLLLLLLLLLLL..........................", str(resource) + '/' + str(resource_id), image_data, image_name)
        returnid = prestashop.add(str(resource) + '/' + str(resource_id), image_data, image_name)
        return returnid

    # @api.multi
    def export_presta_products(self):
        # exports product details,image and variants
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        stock_quanty = self.env['stock.quant']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            query = "select product_id from product_templ_shop_rel_ where shop_id = %s" % shop.id
            self.env.cr.execute(query)
            fetch_shop_products = self.env.cr.fetchall()
            if self.env.context.get('product_ids'):
                product_ids = prod_templ_obj.browse(self.env.context.get('product_ids'))
            else:
                product_ids = prod_templ_obj.search(
                    [('product_to_be_exported', '=', True), ('presta_id', '=', None)])
            print('\nproduct_ids++++++++++++++', product_ids)
            print('\nproduct_ids++++++++++++++', len(product_ids))

            check_list = []
            for temp_data in product_ids:
                check_list.append(temp_data.id)

            new_list = []
            if len(check_list) >= 100:
                new_list = check_list[:100]
            else:
                new_list = check_list

            print('new_list++++++++++++++', new_list)
            print('len+++++++++++', len(new_list))

            # for product in product_ids:
            for prod_id in new_list:

                print("prod_id+_+_++_+prod_id", prod_id)

                product = prod_templ_obj.search([('id', '=', prod_id)])

                product_schema = prestashop.get('products', options={'schema': 'blank'})
                categ = [{'id': product.categ_id.presta_id}]
                position_categ = categ
                parent_id = product.categ_id.parent_id
                print('\nparent_id++++++++++++', parent_id)
                if categ:
                    while parent_id:
                        categ.append({'id': parent_id.presta_id and str(parent_id.presta_id)})
                        parent_id = parent_id.parent_id
                    print("categcate==-=-=-=-=-=-==--", categ)
                    product_schema.get('product').get('associations').update({
                        'categories': {'attrs': {'node_type': 'category'}, 'category': categ},
                    })

                if product.product_spec_ids:
                    feature_values = []
                    for feature_id in product.product_spec_ids:
                        vals = {
                            'id': str(feature_id.feature.presta_id),
                            'id_feature_value': str(feature_id.feature_value.presta_id)
                        }
                        feature_values.append(vals)

                    product_schema.get('product').get('associations').get('product_features').update(
                        {'product_feature': feature_values})

                product_schema.get('product').get('associations').get('stock_availables').update(
                    {'stock_available': {'id': '0', 'id_product_attribute': '0'}})

                website_description_by_languages = []

                # print("SCHEMASCHEMA+_+_+_+_+_+_",product_schema)
                for lang in self.env['prestashop.language'].search([]):
                    odoo_lang = self.env['res.lang'].search([('iso_code', '=', lang.code)])
                    video_url = product.video_url
                    if video_url:

                        insert_video = '<p><iframe width="560" height="315" src="' + video_url + '" frameborder="0"></iframe></p>'
                        insert_video = BeautifulSoup(insert_video, 'lxml')
                        insert_video = insert_video.body.next
                        print("======= insert vid ==========")
                        # print(a.body.next)
                        desc_with_video = str(insert_video) + str(
                            product.with_context(lang=odoo_lang.code).website_description)
                        print(desc_with_video)
                    else:
                        desc_with_video = product.with_context(lang=odoo_lang.code).website_description
                    website_description_by_languages.append(
                        {'attrs': {'id': str(lang.presta_id)},
                         'value': desc_with_video}
                    )

                product_vals = {
                    'name': {'language': {'attrs': {'id': '1'}, 'value': product.name}},
                    'link_rewrite': {'language': {'attrs': {'id': '1'}, 'value': product.name.replace(' ', '-')}},
                    'reference': product.default_code,
                    'price': product.list_price and str(product.list_price) or '0.00',
                    'wholesale_price': str(product.wholesale_price),
                    'depth': str(product.product_lngth),
                    'width': str(product.product_width),
                    'weight': str(product.product_wght),
                    'description': website_description_by_languages,
                    'height': str(product.product_hght),
                    'date_upd': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'date_add': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'active': 1,
                    'state': '1',
                    'type': {'attrs': {'notFilterable': 'true'}, 'value': 'simple'},
                    'id_shop_default': str(self.id),
                    'on_sale': '1',
                    'available_now': ({'language': {'attrs': {'id': '1'}, 'value': product.product_instock and str(
                        int(product.product_instock))}}),

                    # 'quantity': {'attrs': {'notFilterable': 'true'}, 'value': '2'},
                    # 'minimal_quantity': '1',
                    # 'additional_shipping_cost': 20,
                    'position_in_category': {'attrs': {'notFilterable': 'true'}, 'value': '1'},
                    'id_category_default': '2',
                    'visibility': 'both',
                    'available_for_order': '1',
                }

                if product.manufacturer_id.presta_id:
                    print("")
                    product_vals.update({
                        'id_manufacturer': product.manufacturer_id and product.manufacturer_id.presta_id or '0',
                    })
                if product.supplier_id.presta_id:
                    product_vals.update({
                        'id_supplier': product.supplier_id and product.supplier_id.presta_id or '0',
                    })

                print('\nproduct_vals++++++++++++', product_vals)
                product_schema.get('product').update(product_vals)

                print('\nproduct_schema+++++++++++++', product_schema)

                # presta_res = prestashop.add('products', product_schema)
                # print('\npresta_response+++++++++++++', presta_res)

                # p_ids = prdct_obj.search([('product_tmpl_id', '=', product[0].id)])
                product_var_ids = prdct_obj.search([('product_tmpl_id', '=', product.id)])

                presta_res = prestashop.add('products', product_schema)
                presta_id = self.get_value_data(presta_res.get('prestashop').get('product').get('id'))
                product.write({'presta_id': presta_id})
                if product.image_1920:
                    get = self.create_images(prestashop, product.image_1920, presta_id, 'tushar.png')

                # if product.product_template_image_ids:
                #     for images in product.product_template_image_ids:
                #         get = self.create_images(prestashop, images.image_1920, presta_id, 'tushar.png')
                for prod_var in product_var_ids:
                    stck_id = stock_quanty.search(
                        [('product_id', '=', prod_var.id), ('location_id', '=', shop.warehouse_id.lot_stock_id.id)])
                    qty = 0
                    for stck in stck_id:
                        qty += stck.quantity
                    product_comb_schema = prestashop.get('combinations', options={'schema': 'blank'})
                    option_values = []
                    print('\nproduct_template_attribute_value_ids', prod_var.product_template_attribute_value_ids)
                    if prod_var.product_template_attribute_value_ids:
                        # for op in prod_var.product_template_attribute_value_ids:
                        #     print('op++++++++++++++++++', op, op.name)
                        #     option_values.append({'id': op.presta_id})
                        # print('\noption_values++++++++++++', option_values)
                        # product_comb_schema.get('combination').get('associations').get('product_option_values').update({
                        #     'product_option_value': option_values
                        # })
                        product_comb_schema.get('combination').update({
                            'id_product': presta_id,
                            'price': prod_var.combination_price and str(prod_var.combination_price) or '0.00',
                            'reference': prod_var.default_code,
                            'quantity': str(int(prod_var.qty_available)),
                            'minimal_quantity': '1',
                        })
                        print('\nproduct_comb_schema++++++++++++++', product_comb_schema)
                        combination_resp = prestashop.add('combinations', product_comb_schema)
                        print('\ncombination_resp++++++++++++++', combination_resp)
                        c_presta_id = self.get_value_data(
                            combination_resp.get('prestashop').get('combination').get('id'))
                        prod_var.write({
                            'combination_id': c_presta_id,
                        })
                    else:
                        pass
                # self.export_presta_product_inventory()

                product.write({
                    'product_to_be_exported': False,
                })
            shop.env.cr.commit()
            # except Exception as e:
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'export_product_data',
            #              'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context
        return True

    def export_presta_one_product(self, product_id=False):
        # exports product details,image and variants
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        stock_quanty = self.env['stock.quant']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            query = "select product_id from product_templ_shop_rel_ where shop_id = %s" % shop.id
            self.env.cr.execute(query)
            fetch_shop_products = self.env.cr.fetchall()
            if self.env.context.get('product_ids'):
                product_ids = prod_templ_obj.browse(self.env.context.get('product_ids'))
            else:
                product_ids = prod_templ_obj.search(
                    [('product_to_be_exported', '=', True), ('presta_id', '=', None), ('id', '=', product_id)])
            print('\nproduct_ids++++++++++++++', product_ids)
            print('\nproduct_ids++++++++++++++', len(product_ids))

            check_list = []
            for temp_data in product_ids:
                check_list.append(temp_data.id)

            new_list = []
            if len(check_list) >= 100:
                new_list = check_list[:100]
            else:
                new_list = check_list

            print('new_list++++++++++++++', new_list)
            print('len+++++++++++', len(new_list))

            # for product in product_ids:
            for prod_id in new_list:

                print("prod_id+_+_++_+prod_id", prod_id)

                product = prod_templ_obj.search([('id', '=', prod_id)])

                product_schema = prestashop.get('products', options={'schema': 'blank'})
                categ = [{'id': product.categ_id.presta_id}]
                position_categ = categ
                parent_id = product.categ_id.parent_id
                print('\nparent_id++++++++++++', parent_id)
                if categ:
                    while parent_id:
                        categ.append({'id': parent_id.presta_id and str(parent_id.presta_id)})
                        parent_id = parent_id.parent_id
                    print("categcate==-=-=-=-=-=-==--", categ)
                    product_schema.get('product').get('associations').update({
                        'categories': {'attrs': {'node_type': 'category'}, 'category': categ},
                    })

                if product.product_spec_ids:
                    feature_values = []
                    for feature_id in product.product_spec_ids:
                        vals = {
                            'id': str(feature_id.feature.presta_id),
                            'id_feature_value': str(feature_id.feature_value.presta_id)
                        }
                        feature_values.append(vals)

                    product_schema.get('product').get('associations').get('product_features').update(
                        {'product_feature': feature_values})

                product_schema.get('product').get('associations').get('stock_availables').update(
                    {'stock_available': {'id': '0', 'id_product_attribute': '0'}})

                website_description_by_languages = []

                # print("SCHEMASCHEMA+_+_+_+_+_+_",product_schema)
                for lang in self.env['prestashop.language'].search([]):
                    odoo_lang = self.env['res.lang'].search([('iso_code', '=', lang.code)])
                    video_url = product.video_url
                    if video_url:

                        insert_video = '<p><iframe width="560" height="315" src="' + video_url + '" frameborder="0"></iframe></p>'
                        insert_video = BeautifulSoup(insert_video, 'lxml')
                        insert_video = insert_video.body.next
                        print("======= insert vid ==========")
                        # print(a.body.next)
                        desc_with_video = str(insert_video) + str(
                            product.with_context(lang=odoo_lang.code).website_description)
                        print(desc_with_video)
                    else:
                        desc_with_video = product.with_context(lang=odoo_lang.code).website_description
                    website_description_by_languages.append(
                        {'attrs': {'id': str(lang.presta_id)},
                         'value': desc_with_video}
                    )

                product_vals = {
                    'name': {'language': {'attrs': {'id': '1'}, 'value': product.name}},
                    'link_rewrite': {'language': {'attrs': {'id': '1'}, 'value': product.name.replace(' ', '-')}},
                    'reference': product.default_code,
                    'price': product.list_price and str(product.list_price) or '0.00',
                    'wholesale_price': str(product.wholesale_price),
                    'depth': str(product.product_lngth),
                    'width': str(product.product_width),
                    'weight': str(product.product_wght),
                    'description': website_description_by_languages,
                    'height': str(product.product_hght),
                    'date_upd': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'date_add': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    # 'active': 1,
                    'active': product.website_published and '1' or '0',
                    'state': '1',
                    'type': {'attrs': {'notFilterable': 'true'}, 'value': 'simple'},
                    'id_shop_default': str(self.id),
                    'on_sale': '1',
                    'available_now': ({'language': {'attrs': {'id': '1'}, 'value': product.product_instock and str(
                        int(product.product_instock))}}),

                    # 'quantity': {'attrs': {'notFilterable': 'true'}, 'value': '2'},
                    # 'minimal_quantity': '1',
                    # 'additional_shipping_cost': 20,
                    'position_in_category': {'attrs': {'notFilterable': 'true'}, 'value': '1'},
                    'id_category_default': '2',
                    'visibility': 'both',
                    'available_for_order': '1',
                }

                if product.manufacturer_id.presta_id:
                    print("")
                    product_vals.update({
                        'id_manufacturer': product.manufacturer_id and product.manufacturer_id.presta_id or '0',
                    })
                if product.supplier_id.presta_id:
                    product_vals.update({
                        'id_supplier': product.supplier_id and product.supplier_id.presta_id or '0',
                    })

                print('\nproduct_vals++++++++++++', product_vals)
                product_schema.get('product').update(product_vals)

                print('\nproduct_schema+++++++++++++', product_schema)

                # presta_res = prestashop.add('products', product_schema)
                # print('\npresta_response+++++++++++++', presta_res)

                # p_ids = prdct_obj.search([('product_tmpl_id', '=', product[0].id)])
                product_var_ids = prdct_obj.search([('product_tmpl_id', '=', product.id)])

                presta_res = prestashop.add('products', product_schema)
                presta_id = self.get_value_data(presta_res.get('prestashop').get('product').get('id'))
                product.write({'presta_id': presta_id})
                if product.image_1920:
                    get = self.create_images(prestashop, product.image_1920, presta_id, 'tushar.png')

                # if product.product_template_image_ids:
                #     for images in product.product_template_image_ids:
                #         get = self.create_images(prestashop, images.image_1920, presta_id, 'tushar.png')
                for prod_var in product_var_ids:
                    stck_id = stock_quanty.search(
                        [('product_id', '=', prod_var.id), ('location_id', '=', shop.warehouse_id.lot_stock_id.id)])
                    qty = 0
                    for stck in stck_id:
                        qty += stck.quantity
                    product_comb_schema = prestashop.get('combinations', options={'schema': 'blank'})
                    option_values = []
                    print('\nproduct_template_attribute_value_ids', prod_var.product_template_attribute_value_ids)
                    if prod_var.product_template_attribute_value_ids:
                        # for op in prod_var.product_template_attribute_value_ids:
                        #     print('op++++++++++++++++++', op, op.name)
                        #     option_values.append({'id': op.presta_id})
                        # print('\noption_values++++++++++++', option_values)
                        # product_comb_schema.get('combination').get('associations').get('product_option_values').update({
                        #     'product_option_value': option_values
                        # })
                        product_comb_schema.get('combination').update({
                            'id_product': presta_id,
                            'price': prod_var.combination_price and str(prod_var.combination_price) or '0.00',
                            'reference': prod_var.default_code,
                            'quantity': str(int(prod_var.qty_available)),
                            'minimal_quantity': '1',
                        })
                        print('\nproduct_comb_schema++++++++++++++', product_comb_schema)
                        combination_resp = prestashop.add('combinations', product_comb_schema)
                        print('\ncombination_resp++++++++++++++', combination_resp)
                        c_presta_id = self.get_value_data(
                            combination_resp.get('prestashop').get('combination').get('id'))
                        prod_var.write({
                            'combination_id': c_presta_id,
                        })
                    else:
                        pass
                # self.export_presta_product_inventory()

                product.write({
                    'product_to_be_exported': False,
                })
            shop.env.cr.commit()
            # except Exception as e:
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'export_product_data',
            #              'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context
        return True

    # @api.multi
    def export_presta_categories(self):
        categ_obj = self.env['product.category']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            print('\nshop+++++++++++++++', shop.id)
            print('\ncontect+++++++++++++++', self.env.context.get('category_ids'))
            if self.env.context.get('category_ids'):
                category_ids = categ_obj.browse(self.env.context.get('category_ids'))
            else:
                category_ids = categ_obj.search([('to_be_exported', '=', True), ('presta_id', '=', None)])
            print('\ncategory_ids+++++++++++++++++', category_ids)
            for category in category_ids:
                category_schema = prestashop.get('categories', options={'schema': 'blank'})
                category_schema.get('category').update({
                    'name': {'language': {'attrs': {'id': '1'}, 'value': category.name and str(category.name)}},
                    'id_parent': category.parent_id and category.parent_id.presta_id and str(
                        category.parent_id.presta_id) or '0',
                    'link_rewrite': {'language': {'attrs': {'id': '1'},
                                                  'value': category.name and str(category.name.replace(' ', '-'))}},
                    'active': '1',
                    'description': {
                        'language': {'attrs': {'id': '1'}, 'value': category.name and str(category.name)}},
                    'id_shop_default': self.id,
                })
                presta_res = prestashop.add('categories', category_schema)
                if presta_res.get('prestashop').get('category').get('id'):
                    categ_presta_id = self.get_value_data(presta_res.get('prestashop').get('category').get('id'))
                else:
                    categ_presta_id = self.get_value_data(presta_res.get('prestashop').get('id'))
                category.write({
                    'presta_id': categ_presta_id,
                    'to_be_exported': False,
                })
            # except Exception as e:
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'export_categories', 'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context
        return True

    def export_presta_product_inventory(self):
        prodct_templ_obj = self.env['product.template']
        prodct_obj = self.env['product.product']
        stock_quant_obj = self.env['stock.quant']
        # try:
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            self.env.cr.execute("update product_template set prestashop_update_stock= False;")
            product_tmpl_ids = prodct_templ_obj.search([('prestashop_update_stock', '=', False)])
            if product_tmpl_ids:
                for product_tmpl_id in product_tmpl_ids:
                    if product_tmpl_id.presta_id:
                        product_product_ids = prodct_obj.search([('product_tmpl_id', '=', product_tmpl_id.id)])
                        if product_tmpl_id.presta_id:
                            if len(product_product_ids) == 1:
                                stock_quant_ids = stock_quant_obj.search(
                                    [('location_id', '=', shop.warehouse_id.lot_stock_id.id),
                                     ('product_id', '=', product_product_ids.id)])
                                quantity = sum(stock_quant_id.quantity for stock_quant_id in stock_quant_ids)
                                reserved_quantity = sum(
                                    stock_quant_id.reserved_quantity for stock_quant_id in stock_quant_ids)
                                quantity_avilable = quantity - reserved_quantity
                                shop.update_quantity_prestashop(prestashop, product_tmpl_id.presta_id,
                                                                quantity_avilable, shop.presta_id)

                            else:
                                for product_product_id in product_product_ids:
                                    if product_product_id.combination_id:
                                        stock_quant_ids = stock_quant_obj.search(
                                            [('location_id', '=', shop.warehouse_id.lot_stock_id.id),
                                             ('product_id', '=', product_product_id.id)])
                                        quantity_avilable = sum(
                                            stock_quant_id.quantity for stock_quant_id in stock_quant_ids)
                                        combination_id = product_product_id.combination_id
                                        shop.update_quantity_prestashop(prestashop, product_tmpl_id.presta_id,
                                                                        quantity_avilable, shop.presta_id,
                                                                        combination_id)
                        product_tmpl_id.write({'prestashop_update_stock': True})

        # except Exception as e:
        #     if self.env.context.get('log_id'):
        #         log_id = self.env.context.get('log_id')
        #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
        #     else:
        #         log_id_obj = self.env['prestashop.log'].create(
        #             {'all_operations': 'update_inventory', 'error_lines': [(0, 0, {'log_description': str(e), })]})
        #         log_id = log_id_obj.id
        #     new_context = dict(self.env.context)
        #     new_context.update({'log_id': log_id})
        #     self.env.context = new_context

    def export_presta_products_variants(self):
        # exports product details,image and variants
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        stock_quanty = self.env['stock.quant']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            query = "select product_id from product_templ_shop_rel_ where shop_id = %s" % shop.id
            self.env.cr.execute(query)
            fetch_shop_products = self.env.cr.fetchall()
            if self.env.context.get('product_ids'):
                product_ids = prod_templ_obj.browse(self.env.context.get('product_ids'))
            else:
                product_ids = prod_templ_obj.search([('product_to_be_exported', '=', True)])

            print('\nproduct_ids+++++++++++', product_ids)

            for product in product_ids:
                product_schema = prestashop.get('products', options={'schema': 'blank'})
                print('product_schema+_+_+_+_+_+_', product_schema)
                categ = [{'id': product.categ_id.presta_id and str(product.categ_id.presta_id)}]
                print('product.categ_id.parent_id_+_+_+__+', product.categ_id.parent_id)
                parent_id = product.categ_id.parent_id
                while parent_id:
                    categ.append({'id': parent_id.presta_id and str(parent_id.presta_id)})
                    parent_id = parent_id.parent_id
                product_schema.get('product').get('associations').update({
                    'categories': {'attrs': {'node_type': 'category'}, 'category': categ},
                })

                product_schema.get('product').update({
                    'name': {'language': {'attrs': {'id': '1'}, 'value': product.name}},
                    'link_rewrite': {'language': {'attrs': {'id': '1'}, 'value': product.name.replace(' ', '-')}},
                    'reference': product.default_code,
                    'wholesale_price': str(product.wholesale_price),
                    'on_sale': '1',
                    'state': '1',
                    'online_only': '1',
                    'depth': str(product.product_lngth),
                    'width': str(product.product_width),
                    'weight': str(product.product_wght),
                    'height': str(product.product_hght),
                    'price': product.list_price and str(product.list_price) or '0.00',
                    'date_upd': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'date_add': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'active': 1,
                    'available_now': ({'language': {'attrs': {'id': '1'}, 'value': product.product_instock and str(
                        int(product.product_instock))}}),
                    # 					'state': {'value': '1'},
                    # 'type': {'attrs': {'notFilterable': 'true'}, 'value': 'simple'},
                    'id_supplier': product.supplier_id and product.supplier_id.presta_id or '0',
                    'id_manufacturer': product.manufacturer_id and product.manufacturer_id.presta_id or '0',
                    'id_shop_default': self.id,
                    'position_in_category': {'attrs': {'notFilterable': 'true'}, 'value': '1'},
                    'id_category_default': '2',
                })
                product_schema.get('product').get('associations').get('stock_availables').update(
                    {'stock_available': {'id': '0', 'id_product_attribute': '0'}})

                if product.product_spec_ids:
                    feature_values = []
                    for feature_id in product.product_spec_ids:
                        vals = {
                            'id': str(feature_id.feature.presta_id),
                            'id_feature_value': str(feature_id.feature_value.presta_id)
                        }
                        feature_values.append(vals)
                    print('\nfeature_values+++++++++++', feature_values)

                    product_schema.get('product').get('associations').get('product_features').update(
                        {'product_feature': feature_values})

                presta_res = prestashop.add('products', product_schema)
                print('\npresta_res+++++++++++++++', presta_res)

                p_ids = prdct_obj.search([('product_tmpl_id', '=', product[0].id)])
                product_var_ids = prdct_obj.search([('product_tmpl_id', '=', product.id)])
                print('\nproduct_var_ids++++++++++++++', product_var_ids)

                presta_id = self.get_value_data(presta_res.get('prestashop').get('product').get('id'))
                product.write({'presta_id': presta_id})
                if product.image_1920:
                    get = self.create_images(prestashop, product.image_1920, presta_id, 'tushar.png')
                # if product.product_template_image_ids:
                #     for images in product.product_template_image_ids:
                #         get = self.create_images(prestashop, images.image_1920, presta_id, 'tushar.png')
                for prod_var in product_var_ids:
                    stck_id = stock_quanty.search(
                        [('product_id', '=', prod_var.id), ('location_id', '=', shop.warehouse_id.lot_stock_id.id)])
                    qty = 0
                    for stck in stck_id:
                        qty += stck.quantity
                    # product_comb_schema = prestashop.get('combinations',options = {'schema': 'blank'})
                    print(",.,.,.,.,.,.,.,,.,prod_var>>>>>>>>>>>>>>>>>>>>>", prod_var)

                    product_comb_schema = prestashop.get('combinations', options={'schema': 'blank'})
                    # option_values.append({'id': op.id})
                    # product_comb_schema.get('combination').get('associations').get('product_option_values').update({
                    # 	'product_option_value' : option_values
                    # })
                    # print(",.,.,.,.,.,.,.,,.,option_values>>>>>>>>>>>>>>>>>>>>>", option_values)
                    option_values = []
                    for variants_values in prod_var.product_template_attribute_value_ids:
                        # print(",.,.,.,.,.,.,.,,.,variants_values>>>>>>>>>>>>>>>>>>>>>", variants_values.name)
                        value_ids = self.env['product.attribute.value'].search(
                            [('name', '=', variants_values.name)], limit=1)
                        option_values.append({'id': value_ids.presta_id})
                    product_comb_schema.get('combination').update({
                        'id_product': presta_id,
                        'price': prod_var.combination_price and str(prod_var.combination_price) or '0.00',
                        'reference': prod_var.default_code,
                        'quantity': str(int(prod_var.qty_available)),
                        'minimal_quantity': '1',
                        'associations': {'product_option_values': {'product_option_value': option_values}}
                    })
                    # qq
                    combination_resp = prestashop.add('combinations', product_comb_schema)
                    c_presta_id = self.get_value_data(
                        combination_resp.get('prestashop').get('combination').get('id'))
                    print(",.,.,.,.,.,.,.,,.,c_presta_id>>>>>>>>>>>>>>>>>>>>>", c_presta_id)
                    # qqffdgdfhg
                    prod_var.write({
                        'presta_id': c_presta_id,
                        'combination_id': c_presta_id,
                    })
                product.write({
                    'product_to_be_exported': False,
                })
            # except Exception as e:
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'export_product_data',
            #              'error_lines': [(0, 0, {'log_description': 'str(e)', })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context
        return True

    # @api.one
    def search_state(self, prestashop, state_name, country_id):
        # To find the country id in prestashop
        state_obj = self.env['res.country.state']
        state_ids = prestashop.search('states', options={'filter[name]': state_name.name})
        if state_ids:
            state_id = state_ids[0]
        else:
            stats_schema = prestashop.get('states', options={'schema': 'blank'})
            if stats_schema:
                stats_schema.get('state').update({
                    'name': state_name.name,
                    'iso_code': state_name.code,
                    'id_country': country_id,
                })
                stat_res = prestashop.add('states', stats_schema)
                state_id = stat_res.get('prestashop').get('state').get('id').get('value')
        return state_id

    # @api.one
    def search_country(self, prestashop, country_name):
        # To find the country id in prestashop
        country_ids = prestashop.search('countries', options={'filter[name]': country_name.name})
        if country_ids:
            country_id = country_ids[0]
        else:
            country_schema = prestashop.get('countries', options={'schema': 'blank'})
            country_schema.get('country').update({
                'name': {'language': {'attrs': {'id': '1'}, 'value': country_name.name}},
                'iso_code': country_name.code,
                'alias': ''
            })
            country_res = prestashop.add('countries', country_schema)
            country_id = country_res.get('prestashop').get('country').get('id').get('value')
        return country_id

    # @api.multi
    def export_presta_customers(self):
        res_partner_obj = self.env['res.partner']
        for shop in self:
            try:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                query = "select cust_id from customer_shop_rel where shop_id = %s" % shop.id
                self.env.cr.execute(query)
                fetch_shop_customers = self.env.cr.fetchall()
                if self.env.context.get('customer_ids'):
                    customer_ids = res_partner_obj.browse(self.env.context.get('customer_ids'))
                else:
                    customer_ids = res_partner_obj.search([('to_be_exported', '=', True)])
                # 				('id','in',fetch_shop_customers)
                for customer in customer_ids:
                    customer_schema = prestashop.get('customers', options={'schema': 'blank'})
                    customer_name = customer.name
                    name_list = customer_name.split(' ')
                    first_name = name_list[0]
                    if len(name_list) > 1:
                        last_name = name_list[1]
                    else:
                        last_name = name_list[0]
                    dob = customer.date_of_birth

                    customer_schema.get('customer').update({
                        'firstname': first_name and str(first_name),
                        'lastname': last_name and str(last_name),
                        'email': customer.email and str(customer.email),
                        'active': '1',
                        'date_upd': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'date_add': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'birthday': customer.date_of_birth and str(customer.date_of_birth) or False,
                        'website': customer.website and str(customer.website) or '' or False,
                    })
                    presta_cust = prestashop.add('customers', customer_schema)
                    customer_presta_id = self.get_value_data(presta_cust.get('prestashop').get('customer').get('id'))
                    address_schema = prestashop.get('addresses', options={'schema': 'blank'})
                    address_schema.get('address').update({
                        'firstname': first_name and str(first_name),
                        'lastname': last_name and str(last_name),
                        'address1': customer.street and str(customer.street) or '',
                        'address2': customer.street2 and str(customer.street2) or '',
                        'city': customer.city and str(customer.city) or '',
                        'phone': customer.phone and str(customer.phone) or '',
                        'phone_mobile': customer.mobile and str(customer.mobile) or '',
                        'postcode': customer.zip and str(customer.zip) or '',
                        'id_customer': customer_presta_id and str(customer_presta_id),
                        'alias': customer.type and str(customer.type),
                    })
                    if customer.country_id:
                        c_id = shop.search_country(prestashop, customer.country_id)
                        if c_id:
                            address_schema.get('address').update({
                                'id_country': c_id,
                            })
                        # if customer.state_id:
                        # 	address_schema.get('address').update({
                        # 		'id_state': shop.search_state(prestashop, customer.state_id,c_id)
                        # 	})

                    presta_address = prestashop.add('addresses', address_schema)
                    add_presta_id = self.get_value_data(presta_address.get('prestashop').get('address').get('id'))
                    customer.write({
                        'presta_id': customer_presta_id,
                        'to_be_exported': False,
                        'address_id': add_presta_id,
                    })
                    for child in customer.child_ids:
                        address_schema = prestashop.get('addresses', options={'schema': 'blank'})
                        if child.name:
                            name = child.name
                        else:
                            name = customer.name
                        name_list = name.split(' ')
                        first_name = name_list[0]
                        if len(name_list) > 1:
                            last_name = name_list[1]
                        else:
                            last_name = name_list[0]
                        address_schema.get('address').update({
                            'firstname': first_name and str(first_name),
                            'lastname': last_name and str(last_name),
                            'address1': child.street and str(child.street) or '',
                            'address2': child.streets and str(child.street2) or '',
                            'city': child.city and (child.city) or '',
                            'phone': child.phone and str(child.phone) or '',
                            'phone_mobile': child.mobile and str(child.mobile) or '',
                            'postcode': child.zip and str(child.zip) or '',
                            'id_customer': customer_presta_id and str(customer_presta_id),
                            'alias': customer.type and str(customer.type) or ''
                        })
                        if customer.state_id:
                            address_schema.get('address').update({
                                'id_state': shop.search_state(prestashop, child.state_id)
                            })
                        if customer.country_id:
                            c_id = shop.search_country(prestashop, child.country_id)
                            address_schema.get('address').update({
                                'id_country': c_id[0],
                            })
                        presta_address = prestashop.add('addresses', address_schema)
                        add_presta_id = self.get_value_data(presta_address.get('prestashop').get('address').get('id'))
                        child.write({
                            'address_id': add_presta_id,
                            'to_be_exported': False
                        })
            except Exception as e:
                if self.env.context.get('log_id'):
                    log_id = self.env.context.get('log_id')
                    self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
                else:
                    log_id_obj = self.env['prestashop.log'].create(
                        {'all_operations': 'Export_customers', 'error_lines': [(0, 0, {'log_description': str(e), })]})
                    log_id = log_id_obj.id
                new_context = dict(self.env.context)
                new_context.update({'log_id': log_id})
                self.env.context = new_context

    # @api.multi
    def export_presta_customer_messages(self):
        order_msg_obj = self.env['order.message']
        for shop in self:
            try:
                prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                      shop.prestashop_instance_id.webservice_key or None)
                # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
                query = "select mess_id from message_shop_rel where shop_id = %s" % shop.id
                self.env.cr.execute(query)
                fetch_shop_customer_messages = self.env.cr.fetchall()
                if self.env.context.get('customer_message_ids'):
                    customer_message_ids = order_msg_obj.browse(self.env.context.get('customer_message_ids'))
                else:
                    customer_message_ids = order_msg_obj.search([('to_be_exported', '=', True)])

                for customer_message in customer_message_ids:
                    customer_message_schema = prestashop.get('customer_threads', options={'schema': 'blank'})
                    customer_message_schema.get('customer_thread').update({
                        'token': customer_message.token and str(customer_message.token),
                        'email': customer_message.email and str(customer_message.email),
                        'status': customer_message.status and str(customer_message.status),
                        'id_lang': '1',
                        'id_customer': customer_message.customer_id and str(
                            customer_message.customer_id.presta_id) or '0',
                        'id_contact': 0,
                        'id_order': customer_message.new_id and str(customer_message.new_id.presta_id) or '',
                    })
                    customer_threads_res = prestashop.add('customer_threads', customer_message_schema)
                    msg_presta_id = \
                        self.get_value_data(customer_threads_res.get('prestashop').get('customer_thread').get('id'))[0]
                    customer_message.write({
                        'presta_id': msg_presta_id,
                        'to_be_exported': False,
                    })
            except Exception as e:
                if self.env.context.get('log_id'):
                    log_id = self.env.context.get('log_id')
                    self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
                else:
                    log_id_obj = self.env['prestashop.log'].create(
                        {'all_operations': 'export_customer_message',
                         'error_lines': [(0, 0, {'log_description': str(e), })]})
                    log_id = log_id_obj.id
                new_context = dict(self.env.context)
                new_context.update({'log_id': log_id})
                self.env.context = new_context

    # @api.one
    def get_currency(self, prestashop, currency):
        currency_ids = prestashop.search('currencies', options={'filter[iso_code]': currency.name})
        if currency_ids:
            currency_id = currency_ids[0]
        else:
            currency_schema = prestashop.get('currencies', options={'schema': 'blank'})
            currency_schema.get('currency').update({
                'name': currency.name,
                'iso_code': currency.name,
                'sign': currency.name,
                'active': '1',
                'conversion_rate': '1'
            })
            currency_res = prestashop.add('currencies', currency_schema)
            print('\ncurrency_res+++++++++++++', currency_res)
            currency_id = currency_res.get('prestashop').get('currency').get('id').get('value')
        return currency_id

    # @api.one
    def get_languange(self, prestashop, languange):
        lang = self.env['res.lang'].search([('code', '=', languange)])
        languange_ids = prestashop.search('languages', options={'filter[iso_code]': lang.iso_code})
        if languange_ids:
            languange_id = languange_ids[0]
        else:
            languange_schema = prestashop.get('languages', options={'schema': 'blank'})
            languange_schema.get('language').update({
                'name': lang.name,
                'iso_code': lang.iso_code,
                'language_code': lang.code.replace('_', '-'),
                'active': '1',
                'date_format_lite': lang.date_format,
            })
            languange_res = prestashop.add('languages', languange_schema)
            languange_id = self.get_value(languange_res.get('prestashop').get('language'))[0].get('id').get('value')
        return languange_id

    # @api.multi
    def export_presta_orders(self):
        sale_order_obj = self.env['sale.order']
        status_obj = self.env['presta.order.status']
        sale_order_line_obj = self.env['sale.order.line']
        for shop in self:
            # try:
            prestashop = PrestaShopWebServiceDict(shop.shop_physical_url,
                                                  shop.prestashop_instance_id.webservice_key or None)
            # prestashop = PrestaShopWebServiceDict(shop.prestashop_instance_id.location,shop.prestashop_instance_id.webservice_key or None)
            query = "select saleorder_id from saleorder_shop_rel where shop_id = %s" % shop.id
            self.env.cr.execute(query)
            fetch_shop_sale_order = self.env.cr.fetchall()
            if self.env.context.get('ordered_ids'):
                order_ids = sale_order_obj.browse(self.env.context.get('ordered_ids'))
            else:
                order_ids = sale_order_obj.search([('to_be_exported', '=', True)])

            print('\norder_ids+++++++++++++++', order_ids)

            for order in order_ids:
                print('order status', order.order_status, order.order_status.presta_id,
                      str(order.order_status.presta_id))
                order_schema = prestashop.get('orders', options={'schema': 'blank'})
                carts_schema = prestashop.get('carts', options={'schema': 'blank'})
                # lang_schema = prestashop.get('languages',1)
                payment_value = dict(
                    self.env['sale.order'].fields_get(allfields=['pretsa_payment_mode'])['pretsa_payment_mode'][
                        'selection'])[order.pretsa_payment_mode]

                order_schema.get('order').update({
                    'allow_seperated_package': '',
                    'conversion_rate': '1.000000',
                    'current_state': order.order_status and order.order_status.presta_id and str(
                        order.order_status.presta_id),
                    'carrier_tax_rate': '0.000',
                    'date_upd': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'date_add': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'delivery_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'delivery_number': '0',
                    'id_shop': shop.presta_id and str(shop.presta_id),
                    'id_customer': order.partner_id and order.partner_id.presta_id and str(
                        order.partner_id.presta_id),
                    'id_address_delivery': order.partner_id.presta_id and str(order.partner_id.presta_id),
                    'id_address_invoice': order.partner_invoice_id.presta_id and str(
                        order.partner_invoice_id.presta_id),
                    'id_currency': shop.get_currency(prestashop, shop.pricelist_id.currency_id),
                    'id_carrier': order.carrier_prestashop.presta_id and str(order.carrier_prestashop.presta_id),
                    'invoice_number': '0',
                    'id_lang': shop.get_languange(prestashop, order.partner_id.lang),
                    # 'id_shop_group': '1',
                    'mobile_theme': '0',
                    'module': order.pretsa_payment_mode.lower(),
                    'payment': order.pretsa_payment_mode.capitalize(),
                    'round_mode': '0',
                    'round_type': '0',
                    'reference': order.name and str(order.name),
                    'recyclable': '0',
                    # 'shipping_number': {'attrs': {'notFilterable': 'true'}, 'value': ''},
                    'total_paid': '0.000000',
                    'total_paid_real': '0.000000',
                    'total_products': order.amount_total and str(order.amount_total),
                    'total_products_wt': '1.0' or '',
                    'total_discounts': '0.000000',
                    'total_discounts_tax_excl': '0.000000',
                    'total_discounts_tax_incl': '0.000000',
                    'total_paid_tax_excl': '0.000000',
                    'total_paid_tax_incl': '0.000000',
                    'total_shipping': '0.000000',
                    'total_shipping_tax_excl': '0.000000',
                    'total_shipping_tax_incl': '0.000000',
                    'total_wrapping_tax_excl': '0.000000',
                    'total_wrapping_tax_incl': '0.000000',
                    'total_wrapping': '0.000000',
                    'valid': '1',
                })
                if order.invoice_status == 'invoiced':
                    order_schema.get('order').update(
                        {'total_paid_tax_incl': order.amount_total and str(order.amount_total)})
                    order_schema.get('order').update(
                        {'total_paid_tax_excl': order.amount_untaxed and str(order.amount_untaxed)})

                shipping_product = shop.shipment_fee_product_id
                for line in order.order_line:
                    if line.product_id.id == shipping_product.id:
                        shipping_cost = shipping_product.lst_price and str(shipping_product.lst_price)
                        order_schema.get('order').update({'total_shipping': shipping_cost and str(shipping_cost)})
                        order_schema.get('order').update(
                            {'total_shipping_tax_excl': shipping_cost and str(shipping_cost)})
                discount = 0.0
                status_ids = False
                for line in order.order_line:
                    discount += line.discount
                if discount > 0.0:
                    order_schema.get('order').update({'total_discounts': discount and str(discount)})
                    order_schema.get('order').update({'total_discounts_tax_excl': discount and str(discount)})

                if order.order_status.name in ['Awaiting check payment', 'Awaiting bank wire payment',
                                               'Awaiting Cash On Delivery validation', 'Processing in progress']:
                    invoice_not_done = False
                    for invoice in order.invoice_ids:
                        if invoice.state == 'open' or invoice.state == "paid":
                            order_schema.get('order').update(
                                {'invoice_number': invoice.number and str(invoice.number)})
                            order_schema.get('order').update(
                                {'invoice_date': invoice.date_invoice and str(invoice.date_invoice)})
                            order_schema.get('order').update(
                                {'total_paid_real': order.amount_total and str(order.amount_total)})
                        # order.get('order').update({'current_state': str(status_ids[0].presta_id)})
                        else:
                            invoice_not_done = True
                    if invoice_not_done == False:
                        status_ids = status_obj.search([('name', '=', 'Payment accepted')])
                        print('status_ids[0].presta_id', status_ids[0].presta_id)
                        print('status_ids[0].presta_id', str(status_ids[0].presta_id))
                        order_schema.get('order').update(
                            {'current_state': status_ids[0].presta_id and str(status_ids[0].presta_id)})
                        order.order_status = status_ids[0].id

                    picking_not_done = False
                    for picking in order.picking_ids:
                        if picking.state == 'done':
                            order_schema.get('order').update(
                                {'delivery_number': picking.name and str(picking.name)})
                            order_schema.get('order').update(
                                {'delivery_date': picking.scheduled_date and str(picking.scheduled_date)})
                        # order_schema.get('order').update({'current_state': status_ids[0].presta_id and str(status_ids[0].presta_id)})
                        else:
                            picking_not_done = True
                    if picking_not_done == False:
                        status_ids = status_obj.search([('name', '=', 'Shipped')])
                        if status_ids:
                            print('status_ids[0].presta_id', status_ids[0].presta_id)
                            print('status_ids[0].presta_id', str(status_ids[0].presta_id))
                            order_schema.get('order').update(
                                {'current_state': status_ids[0].presta_id and str(status_ids[0].presta_id)})
                            order.order_status = status_ids[0].id
                lines = []
                cart_line_list = []
                if len(order.order_line) > 1:
                    for line in order.order_line:
                        lines.append({
                            'product_attribute_id': line.product_id.combination_id and str(
                                line.product_id.combination_id) or '0',
                            'product_id': line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.presta_id and str(
                                line.product_id.product_tmpl_id.presta_id),
                            'product_name': line.name and str(line.name),
                            'product_price': str(int(line.price_unit)),
                            'product_quantity': str(int(line.product_uom_qty)),
                            'product_reference': line.product_id.default_code and str(line.product_id.default_code),
                        })
                        cart_line_list.append({'id_address_delivery': order.partner_id.address_id and str(
                            order.partner_id.address_id),
                                               'id_product_attribute': line.product_id.combination_id and str(
                                                   line.product_id.combination_id) or '0',
                                               'id_product': line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.presta_id and str(
                                                   line.product_id.product_tmpl_id.presta_id),
                                               'quantity': line.product_uom_qty and str(line.product_uom_qty),
                                               })
                else:
                    line = order.order_line[0]
                    lines = {
                        'product_attribute_id': line.product_id.combination_id and str(
                            line.product_id.combination_id) or '0',
                        'product_id': line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.presta_id and str(
                            line.product_id.product_tmpl_id.presta_id),
                        'product_name': line.name and str(line.name),
                        'product_price': str(int(line.price_unit)),
                        'product_quantity': str(int(line.product_uom_qty)),
                        'product_reference': line.product_id.default_code and str(line.product_id.default_code),
                    }
                    cart_line_list = {
                        'id_address_delivery': order.partner_id.address_id and str(order.partner_id.address_id),
                        'id_product_attribute': line.product_id.combination_id and str(
                            line.product_id.combination_id) or '0',
                        'id_product': line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.presta_id and str(
                            line.product_id.product_tmpl_id.presta_id),
                        'quantity': line.product_uom_qty and str(line.product_uom_qty),
                    }
                order_schema.get('order').get('associations').get('order_rows').update({
                    # 'attrs': {'nodeType': 'order_row',
                    #           'virtualEntity': 'true'},
                    'order_row': lines,
                })
                print('cariier', order.carrier_prestashop and order.carrier_prestashop.presta_id and str(
                    order.carrier_prestashop.presta_id))
                print('delivery', order.partner_id.address_id and str(order.partner_id.address_id))
                carts_schema.get('cart').update({
                    'id_carrier': order.carrier_prestashop and order.carrier_prestashop.presta_id and str(
                        order.carrier_prestashop.presta_id),
                    'id_address_delivery': order.partner_id.presta_id and str(order.partner_id.presta_id),
                    'id_shop': shop.presta_id and str(shop.presta_id),
                    'id_customer': order.partner_id and order.partner_id.presta_id and str(
                        order.partner_id.presta_id),
                    'id_lang': shop.get_languange(prestashop, order.partner_id.lang),
                    'id_address_invoice': order.partner_id.presta_id and str(order.partner_id.presta_id),
                    'id_currency': shop.get_currency(prestashop, shop.pricelist_id.currency_id),
                    # 'id_shop_group' : '1',
                    'mobile_theme': '0',
                    'id_shop': shop.presta_id and str(shop.presta_id),
                    # 'gift': '0',
                    # 'gift_message': '',
                    # 'id_guest': '1',
                })
                carts_schema.get('cart').get('associations').get('cart_rows').update({
                    # 'attrs': {'node_type': 'cart_row',
                    #           'virtual_entity': 'true'},
                    # 'delivery_option': 'a:1:{i:3;s:2:"2,";}',
                    'cart_row': cart_line_list,
                })
                sale_gift_ids = sale_order_line_obj.search([('order_id', '=', order.id), ('gift', '=', True)])
                if sale_gift_ids:
                    for gift_id in sale_gift_ids:
                        gift_msg = gift_id.gift_message
                        wrapping_cost = gift_id.wrapping_cost or '0.000'
                        carts_schema.get('cart').update({
                            'gift': '1',
                            'gift_message': gift_msg and str(gift_msg),
                        })
                        order_schema.get('order').update(
                            {'gift': '1',
                             'gift_message': gift_msg and str(gift_msg),
                             'total_wrapping': wrapping_cost and str(wrapping_cost),
                             'total_wrapping_tax_excl': wrapping_cost and str(wrapping_cost),
                             })
                # print('\norder_schema+++++++++++++++', order_schema)
                print('\carts_schema+++++++++++++++', carts_schema)
                presta_cart = prestashop.add('carts', carts_schema)
                print('\npresta_cart+++++++++', presta_cart)
                cart_presta_id = self.get_value_data(presta_cart.get('prestashop').get('cart').get('id'))[0]
                print('\ncart_presta_id+++++++++', cart_presta_id)
                order.write({
                    'to_be_exported': False
                })
                if cart_presta_id:
                    order_schema.get('order').update({
                        'id_cart': cart_presta_id and str(cart_presta_id),
                    })
                print('\norder_schema+++++++++++++++', order_schema)
                presta_orders = prestashop.add('orders', order_schema)
                print('\npresta_orders++++++++++++++', presta_orders)
            # except Exception as e:
            #     if self.env.context.get('log_id'):
            #         log_id = self.env.context.get('log_id')
            #         self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
            #     else:
            #         log_id_obj = self.env['prestashop.log'].create(
            #             {'all_operations': 'export_order_status',
            #              'error_lines': [(0, 0, {'log_description': str(e), })]})
            #         log_id = log_id_obj.id
            #     new_context = dict(self.env.context)
            #     new_context.update({'log_id': log_id})
            #     self.env.context = new_context

    def action_import_taxes(self):
        account_tax_group_obj = self.env['account.tax.group']
        account_tax_rule_obj = self.env['prestashop.tax.rule']
        account_tax_obj = self.env['account.tax']
        prestashop = PrestaShopWebServiceDict(self.shop_physical_url,
                                              self.prestashop_instance_id.webservice_key or None)
        # prestashop = PrestaShopWebServiceDict(self.prestashop_instance_id.location,self.prestashop_instance_id.webservice_key or None)
        filters = {'display': 'full', 'limit': 1000}
        prestashop_taxes_groups = prestashop.get('tax_rule_groups', options=filters)
        print('\nprestashop_taxes_groups+++++++++++++', prestashop_taxes_groups)
        if type(prestashop_taxes_groups['tax_rule_groups']) == dict:
            if type(prestashop_taxes_groups['tax_rule_groups'].get('tax_rule_group')) == list:
                taxes_group = prestashop_taxes_groups['tax_rule_groups'].get('tax_rule_group')
                if isinstance(taxes_group, list):
                    list_taxes_group = taxes_group
                else:
                    list_taxes_group = [taxes_group]
                for taxes_group in list_taxes_group:
                    odoo_tax_group_id = account_tax_group_obj.search([('presta_id', '=', taxes_group.get('id'))],
                                                                     limit=1)
                    group_vals = {'name': taxes_group.get('name'), 'presta_id': taxes_group.get('id'),
                                  'is_presta': True}
                    if not odoo_tax_group_id:
                        account_tax_group_obj.create(group_vals)
                    else:
                        odoo_tax_group_id.write(group_vals)

        prestashop_taxes = prestashop.get('taxes', options=filters)
        print('\nprestashop_taxes+++++++++++++', prestashop_taxes)
        if type(prestashop_taxes['taxes']) == dict:
            if type(prestashop_taxes['taxes'].get('tax')) == list:
                taxes = prestashop_taxes['taxes'].get('tax')
                if isinstance(taxes, list):
                    list_taxes = taxes
                else:
                    list_taxes = [taxes]
                for taxes in list_taxes:
                    print('\ntaxes+++++++++++++++++++', taxes)
                    odoo_tax_id = account_tax_obj.search(
                        [('is_presta', '=', True), ('presta_id', '=', taxes.get('id'))], limit=1)
                    print('\nodoo_tax_id++++++++++++++++', odoo_tax_id)
                    tax_type = False
                    if self.prestashop_instance_id.tax_type == 'tax_include':
                        tax_type = True
                    vals = {
                        'name': self.action_check_isinstance(taxes.get('name').get('language'))[0].get('value'),
                        'amount': float(taxes.get('rate')),
                        'is_presta': True,
                        'presta_id': taxes.get('id'),
                        'price_include': tax_type,
                        'country_id': 68,
                    }
                    if not odoo_tax_id:
                        account_tax_obj.create(vals)
                    else:
                        odoo_tax_id.write(vals)

        prestashop_taxes_rule = prestashop.get('tax_rules', options=filters)
        if type(prestashop_taxes_rule['tax_rules']) == dict:
            if type(prestashop_taxes_rule['tax_rules'].get('tax_rule')) == list:
                taxes_rule = prestashop_taxes_rule['tax_rules'].get('tax_rule')
                if isinstance(taxes_rule, list):
                    list_taxes_rule = taxes_rule
                else:
                    list_taxes_rule = [taxes_rule]
                for taxes_rule in list_taxes_rule:
                    odoo_tax_rule_id = account_tax_rule_obj.search([('presta_id', '=', taxes_rule.get('id'))], limit=1)
                    odoo_tax_id = account_tax_obj.search(
                        [('is_presta', '=', True), ('presta_id', '=', taxes_rule.get('id_tax'))], limit=1)
                    odoo_group_id = account_tax_group_obj.search(
                        [('presta_id', '=', taxes_rule.get('id_tax_rules_group'))], limit=1)
                    rule_vals = {'presta_id': taxes_rule.get('id'), 'tax_id': odoo_tax_id.id,
                                 'group_id': odoo_group_id.id}
                    if not odoo_tax_rule_id:
                        account_tax_rule_obj.create(rule_vals)
                    else:
                        odoo_tax_rule_id.write(rule_vals)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        self.sale_order_ids = self.env.context.get('active_ids')
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        return res
