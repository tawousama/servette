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

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, date, time
import time
from datetime import timedelta, datetime
import itertools
import logging
import datetime

from odoo.exceptions import UserError
from odoo.tools.translate import _
import psycopg2
from odoo.tools.translate import html_translate
from datetime import timedelta, datetime, date, time

logger = logging.getLogger('__name__')


class product_template(models.Model):
    _inherit = 'product.template'

    @tools.ormcache()
    def _get_default_category_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('product.product_category_all')

    def _read_group_categ_id(self, categories, domain, order):
        category_ids = self.env.context.get('default_categ_id')
        if not category_ids and self.env.context.get('group_expand'):
            category_ids = categories._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    prestashop_product_category = fields.Char('Prestashop Category', size=64)
    prestashop_product_template_id = fields.Many2one("prestashop.instance", string="Prestashop Product Template Id ")

    wholesale_price = fields.Float('Whole Sale Price', digits=(16, 2))
    combination_price = fields.Float(string="Extra Price of combination")
    website_description = fields.Html('Category Description', sanitize_attributes=False, translate=html_translate,
                                      sanitize_form=False)
    prdct_unit_price = fields.Float('Unit Price')
    prestashop_product = fields.Boolean('Prestashop Product')
    product_onsale = fields.Boolean('On sale')
    product_instock = fields.Boolean('In Stock')
    prestashop_update_stock = fields.Boolean('Check Stock Update on Prestashop')
    product_img_ids = fields.One2many('gt.prestashop.product.images', 'product_t_id', 'Product Images')
    prd_label = fields.Char('Label')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    manufacturer_id = fields.Many2one('res.partner', 'Manufacturer')
    tax_group_id = fields.Many2one('account.tax.group', 'Tax Group')
    product_lngth = fields.Float('Length')
    product_wght = fields.Float('Prestashop Weight')
    product_hght = fields.Float('Prestashop Height')
    product_width = fields.Float('Prestashop Width')
    prd_type_name = fields.Char('Product Type Name')
    prest_active = fields.Boolean('Prestashop Active')
    prest_img_id = fields.Integer('Imge ID')
    product_list_id = fields.One2many('product.listing', 'product_id', 'Product Shops')
    presta_id = fields.Char('Prestashop ID', copy=False)
    write_date = fields.Datetime(string="Write Date")
    tmpl_shop_ids = fields.Many2many('prestashop.shop', 'product_templ_shop_rel_', 'product_id', 'shop_id',
                                     string="Prestashop Shops")
    product_category_ids = fields.Many2many('product.category', 'product_template_categ_relation', 'product_id',
                                            'categ_id', string="Category", domain="[('presta_id','!=',False)]")
    presta_categ_ids = fields.Many2many('product.category', domain="[('presta_id','!=',False)]")
    product_shop_count = fields.Integer(string="Shops", compute='get_product_shop_count', default=0)
    product_to_be_exported = fields.Boolean(string="Product to be exported?")
    sku = fields.Char(string="SKU")

    product_to_be_updated = fields.Boolean('Update On Prestashop')
    odoo_categ_id = fields.Many2one('product.category', string="Odoo Category")
    presta_price = fields.Float()
    show_price = fields.Boolean(default=True)
    condition = fields.Selection([
        ('new', 'In Stock'),
        ('nouveaute', 'New Product'),
        ('occasion', 'Second Hand'),
        ('deal', 'Deal'),
        ('sold', 'Sold'),
        ('vintage', 'Vintage and Rare'),
        ('promo', 'Promo'),
    ], default='nouveaute')
    website_meta_title = fields.Char("Website meta title", translate=True)
    website_meta_description = fields.Text("Website meta description", translate=True)
    website_meta_keywords = fields.Char("Website meta keywords", translate=True)
    seo_name = fields.Char("Seo name", translate=True)
    website_published = fields.Boolean('Available on the Website', copy=False)
    summary = fields.Html(translate=True, sanitize=False)
    sp_eacute_specifications_techniques = fields.Html('Technical Specifications', translate=True, sanitize=False)
    demande_catalogue = fields.Char('Price on request / Catalog price', translate=True)
    video_url = fields.Char("URL Vidéo", copy=True)
    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, default=_get_default_category_id, group_expand='_read_group_categ_id',
        required=False)

    def write(self, vals):
        print('self+++++++++++++', self)
        logger.info("=======> write  vals %s " % vals.keys())
        # Code upd added for sync img to presta after
        if len(self) == 1:
            skip_write_control = self.env.context.get('skip_write_control', False)
            if not skip_write_control:
                if 'image_1920' in vals:
                    product_img = self.product_img_ids.filtered(lambda p: p.is_default_img)
                    logger.info("=======> product_img %s" % product_img)

                    self.prest_img_id = 0
                    if self.product_img_ids and product_img:
                        logger.info("=======> found vals product_img")
                        if vals['image_1920']:
                            product_img.write({
                                'image': vals['image_1920'].encode('utf-8'),
                                'file_db_store': vals['image_1920'].encode('utf-8'),
                                'image_to_update': True,
                            })
                        else:
                            product_img.unlink()
                    else:
                        logger.info("=======> Not found vals product_img")
                        if vals['image_1920']:
                            img_vals = {'is_default_img': True,
                                        'prest_img_id': 0,
                                        'image': vals['image_1920'].encode('utf-8') if vals['image_1920'] else False,
                                        'file_db_store': vals['image_1920'].encode('utf-8') if vals['image_1920'] else False,
                                        'prest_product_id': self.presta_id,
                                        'name': '-',
                                        'product_t_id': self.id}
                            self.env['gt.prestashop.product.images'].create(img_vals)

        res = super(product_template, self).write(vals)
        curent_date = datetime.now()
        for selfId in self:
            self_id = selfId.id
            query = "UPDATE product_template SET write_date='%s' where id = %s" % (curent_date, self_id)
            self.env.cr.execute(query)
        logger.info('write done')
        return res

    def copy(self, default=None):
        self.ensure_one()
        new = super().copy(default)
        new.product_to_be_exported = True
        return new

    # Ganesh code
    # x_etapa_de_vida = fields.Selection(
    #     [('Cachorro', 'Cachorro'), ('Adulto', 'Adulto'), ('Senior', 'Senior'), ('Todos', 'Todos')],
    #     string='Etapa de vida')
    # x_tamano_de_raza = fields.Selection(
    #     [('Toy', 'Toy'), ('Pequenos', 'Pequenos'), ('Medianos', 'Medianos'), ('Grandes', 'Grandes'),
    #      ('Gigantes', 'Gigantes'), ('Todas', 'Todas')], string='Tamaño de raza')
    # x_peso_de_mascota = fields.Selection(
    #     [('2-3kgs', '2-3kgs'), ('3-5kgs', '3-5kg'), ('5kg-mas', '5kg-mas')],
    #     string='Peso de mascota')
    # x_entrega_en_tienda = fields.Boolean('Entrega en tienda')
    # x_delivery_mismo_dia = fields.Boolean('Delivery mismo dia')
    # x_delivery_programado = fields.Boolean('Delivery programado')
    # x_suscripcion = fields.Boolean('Suscripción')
    # x_influencer_1 = fields.Char('Influencer 1')
    # x_influencer_2 = fields.Char('Influencer 2')
    # x_influencer_3 = fields.Char('Influencer 3')

    product_spec_ids = fields.One2many('product.spec', 'product_tmpl_id', 'Specification')

    def get_product_shop_count(self):
        for temp in self:
            temp.product_shop_count = len(temp.tmpl_shop_ids)

    # @api.multi
    def action_get_shop_product(self):
        action = self.env.ref('prestashop_connector_gt.act_prestashop_shop_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            # 'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'domain': [('id', 'in', self.tmpl_shop_ids.ids)]
        }

        return result

    def action_update_prestashop_product(self):
        self.ensure_one()
        for shop in self.tmpl_shop_ids:
            # print("shop =>", shop)
            try:
                # shop.update_products(shop)
                shop.update_one_product(shop, self.id)
                self.message_post(body='The product is updated on Prestashop')
            except Exception as e:
                raise UserError('Prestashop error: %s' % e)

    def action_fix_product_image(self):
        self.ensure_one()
        for shop in self.tmpl_shop_ids:
            try:
                shop.fix_product_image(self)
                self.message_post(body='The product default image "prest_img_id" is fixed on odoo')
            except Exception as e:
                raise UserError('Prestashop error: %s' % e)

    def action_export_to_prestashop(self):
        self.ensure_one()
        for shop in self.tmpl_shop_ids:
            try:
                # prestashop = shop.presta_connect(True)
                shop.export_presta_one_product(self.id)
                # shop.export_presta_products()
                self.message_post(body='The product is exported to Prestashop')

            except Exception as e:
                raise UserError('Prestashop error: %s' % e)


# product_template()


class product_specification(models.Model):
    _name = 'product.spec'

    feature = fields.Many2one('product.feature', 'Feature')
    feature_value = fields.Many2one('product.feature.value', 'Value')
    product_tmpl_id = fields.Many2one('product.template', 'Template Id')


class product_feature(models.Model):
    _name = 'product.feature'

    presta_id = fields.Char('Presta Id')
    position = fields.Char('Position')
    name = fields.Char('Feature Name')
    features_value_ids = fields.One2many('product.feature.value', 'feature_id', 'Feature Value')


class product_feature_value(models.Model):
    _name = 'product.feature.value'

    presta_id = fields.Char('Presta Id')
    feature_id = fields.Many2one('product.feature', 'Feature Id')
    name = fields.Char('Feature Value Name')


class product_product(models.Model):
    _inherit = 'product.product'

    prestashop_product = fields.Boolean('Prestashop Product')
    # shop_ids = fields.Many2many('prestashop.shop', 'product_prod_shop_rel', 'product_prod_id', 'shop_id', string="Shop")
    presta_id = fields.Char('Presta ID')
    prestashop_product_id = fields.Many2one("prestashop.instance", string="Prestashop Product Id ")

    combination_price = fields.Float(string="Extra Price of combination")
    combination_id = fields.Char(string="Combination ID")
    presta_inventory_id = fields.Char(string='Presta inventory ID')

    prodshop_ids = fields.Many2many('prestashop.shop', 'product_prod_shop_rel', 'product_prod_id', 'shop_id',
                                    string="Shop")


#     presta_id = fields.Char('Presta ID')

class product_attribute(models.Model):
    _inherit = 'product.attribute'

    is_presta = fields.Boolean("Is Prestashop")
    public_name = fields.Boolean("Public Name")
    presta_id = fields.Char(string='Presta Id')
    shop_ids = fields.Many2many('prestashop.shop', 'attr_shop_rel', 'attr_id', 'shop_id', string="Shop")


class product_attribute_value(models.Model):
    _inherit = "product.attribute.value"

    _sql_constraints = [
        ('value_company_uniq', 'CHECK(1=1)', 'You cannot create two values with the same name for the same attribute.')]

    is_presta = fields.Boolean("Is Prestashop")
    presta_id = fields.Char(string='Presta Id')
    write_date = fields.Datetime(string="Write Date")
    shop_ids = fields.Many2many('prestashop.shop', 'attr_val_shop_rel', 'attr_val_id', 'shop_id', string="Shop")


class product_category(models.Model):
    _inherit = "product.category"
    presta_id = fields.Char("Presta ID")
    sequence = fields.Integer('Sequence', default=1, help="Assigns the priority to the list of product Category.")
    write_date = fields.Datetime(string="Write Date")
    is_presta = fields.Boolean("Is Prestashop")
    active = fields.Boolean("Active", default=True)
    friendly_url = fields.Char("Friendly URL")
    meta_title = fields.Char("Meta Title", size=70)
    meta_description = fields.Text("Meta description", )
    shop_id = fields.Many2one('prestashop.shop', 'Shop ID')
    shop_ids = fields.Many2many('prestashop.shop', 'categ_shop_rel', 'categ_id', 'shop_id', string="Shop")
    to_be_exported = fields.Boolean(string="To be exported?")


class product_listing(models.Model):
    _name = 'product.listing'
    _description = 'Product Listing'

    shop_id = fields.Many2one('prestashop.shop', 'Shop ID')
    product_id = fields.Many2one('product.template', 'product_id')


class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'
    write_date = fields.Datetime(string="Write Date")
    presta_id = fields.Char("Presta ID")
    shop_ids = fields.Many2many('prestashop.shop', 'stockware_shop_rel', 'stockware_id', 'shop_id', string="Shop")


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    presta_id = fields.Char("Presta ID")
    is_presta = fields.Char("Presta stock")

    @api.model
    def _get_inventory_fields_create(self):
        res = super(stock_quant, self)._get_inventory_fields_create()
        res.append('presta_id')
        res.append('is_presta')
        return res
