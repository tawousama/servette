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


import logging
logger = logging.getLogger('stock')
from odoo import api, fields, models, _
from odoo.addons.prestashop_connector_gt.prestapyt.prestapyt import PrestaShopWebServiceDict as PrestaShopWebServiceDict
# from odoo.addons.prestashop_connector_gt.prestapyt_old.prestapyt import PrestaShopWebServiceDict as PrestaShopWebServiceDict
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    select_instance = fields.Many2one("prestashop.instance", string="Select Instance")
    sales_team = fields.Many2one("crm.team", string="Sales Team")
    sales_person = fields.Many2one("res.users", string="Salesperson")
    sale_order_prefix = fields.Char("Sales Order Prefix")
    tags = fields.Many2many("crm.tag", string="Tags")
    prestashop_store_view_id = fields.Many2one("prestashop.shop", string="Storeviews")
    is_use_odoo_order_sequence_prestashop = fields.Boolean(
        "Is Use Odoo Order Sequences?",
        default=False,
        help="If checked, Odoo Order Sequence is used when import and create orders.")

    # import_order_status = fields.Selection([('pending', 'Pending'), ('successful', 'Successful')])
    # import_order_after_date = fields.Datetime("Import Order After Date")

    def action_create_more_instance(self):
        print("Test button clicked..")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        data = int(self.env['ir.config_parameter'].sudo().get_param('sales_team'))
        sale_pers = int(self.env['ir.config_parameter'].sudo().get_param('sales_person'))
        # store_view = int(self.env['ir.config_parameter'].sudo().get_param('prestashop_store_view_id'))
        # insta = int(self.env['ir.config_parameter'].sudo().get_param('select_instance'))

        res.update(
            sales_team=data,
            sales_person=sale_pers,
            # prestashop_store_view_id=store_view,
            sale_order_prefix=self.env['ir.config_parameter'].sudo().get_param('sale_order_prefix')
            # select_instance=insta
        )
        return res

    def set_values(self):
        print("tdddddddddddddv", self.sales_person.name)
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        team = self.sales_team.id or False
        sale_pers = self.sales_person.id or False
        order_prefix = self.sale_order_prefix or False
        store_view_id = self.prestashop_store_view_id.id or False
        # instance = self.select_instance.id or False

        param.set_param('sales_team', team)
        param.set_param('sales_person', sale_pers)
        param.set_param('sale_order_prefix', order_prefix)
        param.set_param('prestashop_store_view_id', store_view_id)
        # param.set_param('select_instance', instance)


class prestashop_instance(models.Model):
    _name = 'prestashop.instance'
    _description = 'Prestashop Instance'

    def _select_versions(self):
        """ Available versions
        Can be inherited to add custom versions.
        """
        return [('1.7', '1.7')]


    name = fields.Char('Name')
    version = fields.Selection(_select_versions,string='Version',required=True, default='1.7')
    location = fields.Char('Location',default='http://localhost/prestashop',required=True)
    webservice_key = fields.Char('Webservice key',help="You have to put it in 'username' of the PrestaShop ""Webservice api path invite",required=True)
    warehouse_id=fields.Many2one('stock.warehouse','Warehouse', help='Warehouse used to compute the stock quantities.')
    company_id= fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    shipping_product_id=fields.Many2one('product.product', 'Shipping Product')
    included_tax=fields.Boolean('Tax Include?', help='If this check box are false tax consider as excluded')
    tax_type = fields.Selection([('tax_include','Tax Include?'),('tax_exclude','Tax Exclude?')], string='Tax Consider in Odoo', default='tax_exclude')
    mapped_product_by = fields.Selection([('presta_id','Prestashop Id'),('default_code','Refrence'),('barcode','Barcode')], string='Mapped Product By', default='presta_id')
#     Count Button For Sale Shop
    presta_id = fields.Char(string='shop Id')
    sale_shop_count = fields.Integer(string='Shops\s Count', compute='get_shop_count', default=0)

    def wizard_function(self):
        id = self.env['prestashop.instance'].search([])
        if not len(id) > 1:
            vals = {
                "prestashops_instance_ids": [(4, id.id)],

            }
            if not id:
                raise ValidationError(_('First create the Instance'))
        else:
            vals = {}

        wizard_id = self.env['gt.prestashop.import.export'].create(vals)
        return {
            'name': _('Operations'),
            'type': 'ir.actions.act_window',
            'res_model': 'gt.prestashop.import.export',
            'view_id': self.env.ref('prestashop_connector_gt.view_prestashop_import_export_operation').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard_id.id,
        }


    def prestashop_test_connection(self):
        """
                This method check connection in prestashop.
                """
        # This will make sure we have on record, not multiple records.
        self.ensure_one()
        try:
            prestashop = PrestaShopWebServiceDict(self.location, self.webservice_key or None)
            prestashop_product_data = prestashop.get('shops')
        except Exception as error:
            raise UserError(
                _("Connection Test Failed! Here is what we got instead:\n \n%s") % UserError(error))
        if prestashop_product_data:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': "Connection Test Succeeded! Everything seems properly set up!",
                    'img_url': '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }

    # @api.multi
    @api.depends('presta_id')
    def get_shop_count(self):
        sale_shop_obj = self.env['prestashop.shop']
        res = {}
        for shop in self:
            multishop_ids = sale_shop_obj.search([('prestashop_instance_id', '=', shop.id)])
            shop.sale_shop_count = len(multishop_ids.ids)
            # print "yhihh====>",len(multishop_ids.ids)
        return res

    # @api.multi
    def action_get_sale_shop(self):
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
        }

        return result

    # @api.one
    def create_shop(self, shop_val):
        sale_shop_obj = self.env['prestashop.shop']
        price_list_obj = self.env['product.pricelist']
        journal_obj = self.env['account.journal']
        company_obj = self.env['res.company']
        warehouse_obj = self.env['stock.warehouse']
        product_temp_obj = self.env['product.template']
        product_prod_obj = self.env['product.product']
        presta_instance_obj = self.env['prestashop.instance']
        # location_route_obj = self.env['stock.location.route']
        workflow_obj = self.env['import.order.workflow']
        res_partner_obj = self.env['res.partner']
        shop_obj = self.env['prestashop.shop']

        def_journal_ids = journal_obj.search([('type', '=', 'bank')])
        def_pricelist_ids = price_list_obj.search([])
#         def_route_ids = location_route_obj.search([('name','=',"Make To Order")])
        def_workflow_ids = workflow_obj.search([('name','=','Basic Workflow')])
        def_partner_ids = res_partner_obj.search([('name','=','Guest'),('company_type','=','person')])
        company_ids = company_obj.search([])
        def_ship_ids = product_prod_obj.search([('type', '=', 'service'),('name','like','%Shipping%')])
        def_gift_ids = product_prod_obj.search([('type', '=', 'service'), ('name', 'like', '%Gift%')])
        def_free_discount = product_prod_obj.search([('type', '=', 'service'), ('name', 'like', '%Discount%')])
        def_warehouse_ids = warehouse_obj.search([])

        shop_vals = {
            # 'name' : shop_val.get('name').get('value'),
            'name' : self.get_value_data(shop_val.get('name')),

            'prestashop_instance_id' : self.id,
            'prestashop_shop' : True,
            'shop_physical_url': self.location,
            # 'presta_id': shop_val.get('id').get('value'),
            'presta_id': self.get_value_data(shop_val.get('id'))[0],

            'pricelist_id': def_pricelist_ids and def_pricelist_ids[0].id,
            'sale_journal': def_journal_ids and def_journal_ids[0].id,
            'company_id': company_ids and company_ids[0].id,
            'shipment_fee_product_id': def_ship_ids and def_ship_ids[0].id,
            'gift_wrapper_fee_product_id': def_gift_ids and def_gift_ids[0].id,
            'discount_product_id': def_free_discount and def_free_discount[0].id,
            'warehouse_id' : def_warehouse_ids and def_warehouse_ids[0].id,
            # 'prefix': shop_val.get('name').get('value'),
            'prefix': self.get_value_data(shop_val.get('name')),

#             'route_ids': [(6,0,[def_route_ids[0].id])],
            'partner_id' : def_partner_ids and def_partner_ids[0].id,
            'workflow_id': def_workflow_ids and def_workflow_ids[0].id,
        }
        # shop_ids = sale_shop_obj.search([('prestashop_instance_id', '=', self[0].id), ('name', '=', shop_val.get('name').get('value'))])
        shop_ids = sale_shop_obj.search([('prestashop_instance_id', '=', self[0].id),('name', '=', self.get_value_data(shop_val.get('name'))[0])])

        if not shop_ids:
            sale_shop_id = sale_shop_obj.create(shop_vals)
#             sale_shop_id.import_product_attributes()
        else:
            sale_shop_id = shop_ids
        return sale_shop_id

    # @api.one
    def get_value_data(self, value):
      if isinstance(value, dict):
          return value.get('value')
      else:
          return value

    # @api.multi
    def create_prestashop_shop_action(self):
        try:

            lang_obj = self.env['prestashop.language']
            sale_shop_obj = self.env['prestashop.shop']
            shop_ids = []
            for instance in self:
                prestashop = PrestaShopWebServiceDict(instance.location, instance.webservice_key)
                print('ORrdfggINSTAUGUHIJOPJ', prestashop)
                shops = prestashop.get('shops')
                # print "instance.shop_physical_url=====>",instance.shop_physical_url

                if shops.get('shops') and shops.get('shops').get('shop'):
                    shops = shops.get('shops').get('shop')
                    if isinstance(shops, list):
                       shops_val = shops
                    else:
                       shops_val = [shops]

                    for shop_id in shops_val:
                       id = shop_id.get('attrs').get('id')
                       data = prestashop.get('shops', id)
                       if data.get('shop'):
                           shop_id = sale_shop_obj.search([('presta_id','=',self.get_value_data(data.get('shop').get('id'))[0])])
                           if not shop_id:
                                shop_ids.append(instance.create_shop(data.get('shop')))

                    languages = prestashop.get('languages')
                    lan_vals = languages.get('languages').get('language')
                    if isinstance(lan_vals, list):
                        lan_vals = languages.get('languages').get('language')
                    else:
                        lan_vals = [languages.get('languages').get('language')]
                    for lang in lan_vals:
                        logger.info('lang ===> %s', lang)
                        lang_vals = prestashop.get('languages', lang.get('attrs').get('id'))
                        logger.info('lang_vals===> %s', lang_vals)
                       # vals = {
                       #     'name': lang_vals.get('language').get('name').get('value'),
                       #     'code': lang_vals.get('language').get('iso_code').get('value'),
                       #     'presta_id' : lang_vals.get('language').get('id').get('value'),
                       #     'presta_instance_id' : instance.id
                       # }
                        vals = {
                           'name': self.get_value_data(lang_vals.get('language').get('name')),
                           'code': self.get_value_data(lang_vals.get('language').get('iso_code')),
                           'presta_id' : self.get_value_data(lang_vals.get('language').get('id')),
                           'presta_instance_id' : instance.id
                        }
                       # l_ids = lang_obj.search([('presta_id','=', lang_vals.get('language').get('id').get('value')),('presta_instance_id','=', instance.id)])
                        l_ids = lang_obj.search([('presta_id','=', self.get_value_data(lang_vals.get('language').get('id'))[0]),('presta_instance_id','=', instance.id)])
                        if not l_ids:
                            lang_obj.create(vals)
    #                 if shop_ids:
    #                     shop_ids.import_product_attributes()
        except Exception as e:
            raise ValidationError(_(str(e)))

        if prestashop:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': "Shop has been created! Everything seems properly set up!",
                    'img_url': '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
