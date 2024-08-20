import time
# from odoo.addons.prestashop_connector_gt.prestashop_api import amazonerp_osv as amazon_api_obj
from odoo import api, fields, models, _


class PrestashopConnectorWizard(models.Model):
    _name = "prestashop.connector.wizard"
    _description = 'Prestashop Connector Wizard'

    @api.model
    def default_get(self, fields_list):
        result = super(PrestashopConnectorWizard, self).default_get(fields_list)
        if self._context.get('active_model') == 'prestashop.shop':
            obj = self.env['prestashop.shop'].browse(self._context.get('active_id'))
            result.update({'shop_ids': self._context.get('active_ids'),
                           'last_order_import_date': obj.last_prestashop_order_import_date})
        return result

    shop_ids = fields.Many2many('prestashop.shop', string="Select Shops")
    # import fields
    # import_orders_status = fields.Boolean('Import Orders Status.')
    import_orders = fields.Boolean('Import Orders')
    import_orders_status = fields.Boolean('Import Orders Status')
    import_country_state = fields.Boolean('Import Country/State')
    last_order_import_date = fields.Datetime('Last presta order Import Date')
    import_products = fields.Boolean('Import Products')
    import_products_images = fields.Boolean('Import Products Images')
    import_categories = fields.Boolean('Import Categories')
    import_customers = fields.Boolean('Import Customers',
                                      help='Import 2000 customer from prestashop to odoo at time and last import prestashop customer id store in shop. ')
    count_import = fields.Integer('Total Import Record', default=0)
    last_customer_id_import = fields.Integer('Last ID Import', default=0)
    import_suppliers = fields.Boolean('Import Suppliers')
    import_manufacturers = fields.Boolean('Import Manufacturers')
    import_taxes = fields.Boolean('Import Taxes')
    # import_tax_rules = fields.Boolean('Import Tax Rules')
    import_addresses = fields.Boolean('Import Addresses')
    import_product_attributes = fields.Boolean('Import Products Attributes',
                                               help="Includes Product Attributes and Categories")
    import_inventory = fields.Boolean('Import Inventory')
    import_carriers = fields.Boolean('Import Carriers')
    import_messages = fields.Boolean("Import Messages")
    import_cart_rules = fields.Boolean("Import Cart Rules")
    import_catalog_rules = fields.Boolean("Import Catalog Rules")
    # update fields
    update_categories = fields.Boolean("Update Categories")
    update_cart_rules = fields.Boolean('Update Cart Rules')
    update_catalog_rules = fields.Boolean("Upload Catalog Rules")
    update_product_data = fields.Boolean('Update Product Data')
    update_product_price = fields.Boolean('Update Product Price')
    update_presta_product_inventory = fields.Boolean(string="Update Product Inventory")
    update_order_status = fields.Boolean('Update Order Status')

    update_product_feature = fields.Boolean('Update Product Feature')

    export_presta_customers = fields.Boolean(string="Export Customers")
    export_presta_customer_messages = fields.Boolean(string="Export Customer Messages")
    export_presta_orders = fields.Boolean(string="Export Orders")
    export_presta_products = fields.Boolean(string="Export Products")
    export_presta_products_variants = fields.Boolean(string="Export Products Variants")
    export_presta_product_inventory = fields.Boolean(string="Export Product Inventory")
    export_presta_categories = fields.Boolean(string="Export Categories")

    import_product_fetures = fields.Boolean(string="Import Product Feature")

    # @api.model
    # def default_get_data(self, fields):
    #     result = super(AmzonConnectorWizard, self).default_get_data(fields)
    #     if self._context.get('active_model') == 'prestashop.shop':
    #         print(" self._context.get+_+_+_+_+__+_+__", self._context.get)
    #         result.update({'shop_ids': self._context.get('active_ids')})
    #     return result
    # @api.model
    # def shop_data_wizard(self):
    #     id = self.env['prestashop.shop'].search([])
    #     print("ID+_+_+_+_id+_+_+_+", len(id), id.id, type(id.id))
    #     if not len(id) > 1:
    #         vals = {
    #             "shop_ids": [(4, id.id)],
    #         }
    #     else:
    #         vals = {}
    #
    #     print("vals+_+_+_+_+_+_+__+", vals)
    #     wizard_id = self.env['prestashop.connector.wizard'].create(vals)
    #     print("wizard_id+++_+_+_+_+_++", wizard_id.id)
        # return {
        #     'name': _('Accessories'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'gt.prestashop.import.export',
        #     'view_id': self.env.ref('prestashop_connector_gt.view_import_prestashop_connector_wizard_form_view').id,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'res_id': wizard_id.id,
        # }

    # @api.one
    def import_prestashop(self):
        shop_ids = self.shop_ids

        if self.import_product_attributes:
            for shop_id in shop_ids:
                shop_id.import_product_attributes()

        if self.import_categories:
            self.shop_ids.import_categories()

        if self.import_customers:
            self.shop_ids.import_customers()

        if self.import_suppliers:
            self.shop_ids.import_suppliers()

        if self.import_manufacturers:
            self.shop_ids.import_manufacturers()

        if self.import_country_state:
            self.shop_ids.import_country_state()
        if self.import_taxes:
            self.shop_ids.action_import_taxes()
        #
        # if self.import_tax_rules:
        #     self.shop_ids.import_tax_rules()

        if self.import_addresses:
            self.shop_ids.import_addresses()

        if self.import_products:
            for shop_id in shop_ids:
                shop_id.import_products()

        if self.import_products_images:
            for shop_id in shop_ids:
                shop_id.import_products_images()

        if self.import_inventory:
            for shop_id in shop_ids:
                shop_id.import_product_inventory()

        if self.import_carriers:
            for shop_id in shop_ids:
                shop_id.import_carriers()

        if self.import_orders_status:
            for shop_id in shop_ids:
                shop_id.import_orders_status()

        if self.import_orders:
            for shop_id in shop_ids:
                shop_id.import_orders()

        if self.import_messages:
            for shop_id in shop_ids:
                shop_id.import_messages()

        if self.import_cart_rules:
            for shop_id in shop_ids:
                shop_id.import_cart_rules()

        if self.import_catalog_rules:
            for shop_id in shop_ids:
                shop_id.import_catalog_price_rules()

        if self.import_product_fetures:
            self.shop_ids.import_product_fetures()

        if self.update_order_status:
            for shop_id in shop_ids:
                shop_id.update_order_status()

        if self.export_presta_products_variants:
            self.shop_ids.export_presta_products_variants()
        #
        if self.update_categories:
            self.shop_ids.update_prestashop_category()
        #             for shop_id in shop_ids:
        #                 presta_instance_id=shop_id.prestashop_instance_id
        #                 prestashop=self.env['prestashop.shop'].browse(presta_instance_id.id).presta_connect_json()
        #                 categ_list=self.env['prestashop.category'].search([('shop_id','=',shop_id.id)])
        # #                 categ_list=[categ_id.id for categ_id in categ_list]
        #                 self.env['prestashop.upload.products'].upload_categories(prestashop,categ_list)

        if self.update_cart_rules:
            self.shop_ids.update_cart_rules()
            # for shop_id in shop_ids:
            #     cart_rule_ids=self.env['cart.rules'].search([('prestashop_id','=',shop_id.id)])
            #     cart_rule_ids=[cart_id.id for cart_id in cart_rule_ids]
            #     presta_instance_id=shop_id.prestashop_instance_id
            #     self.env['upload.cart.rule'].create({}).upload_cart_rule(False,cart_rule_ids,presta_instance_id)
        if self.update_catalog_rules:
            self.shop_ids.update_catalog_rules()

        if self.update_product_price:
            self.shop_ids.update_product_price()

        if self.update_product_data:
            self.shop_ids.update_products()

        if self.update_product_feature:
            self.shop_ids.update_products_feature()

        if self.update_presta_product_inventory:
            self.shop_ids.update_presta_product_inventory()

        if self.export_presta_customers:
            self.shop_ids.export_presta_customers()

        if self.export_presta_customer_messages:
            self.shop_ids.export_presta_customer_messages()

        if self.export_presta_categories:
            self.shop_ids.export_presta_categories()

        if self.export_presta_products:
            self.shop_ids.export_presta_products()

        if self.export_presta_orders:
            self.shop_ids.export_presta_orders()

        if self.export_presta_product_inventory:
            self.shop_ids.export_presta_product_inventory()

        return True
