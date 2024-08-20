from odoo import fields, models, api
from odoo.tools.translate import _
import xml.etree.ElementTree as ET
from odoo.exceptions import Warning


class CreatePrestashopShop(models.TransientModel):
    _name = "create.prestashop.shop"
    _description = "Create Prestashop Shop"

    def view_init(self, fields_list):
        if self._context is None:
            self._contex = {}
        res = super(CreatePrestashopShop, self).view_init(fields_list)
        active_ids = self._context.get('active_ids', [])
        if active_ids:
            search_shop = self.env['prestashop.shop'].search([('prestashop_instance_id', '=', active_ids[0])])
            if search_shop:
                raise Warning(_('Shop Is Already Created'))
        return res

    def create_prestashop_action(self):
        print("dhhdkn", self.id)
        vals = {
            "name": self.name,
            "version": self.version,
            "company_id": self.company_id.id,
            "webservice_key": self.webservice_key,
            "location": self.location,
            "warehouse_id": self.warehouse_id.id,
            "mapped_product_by": self.mapped_product_by,
            "tax_type": self.tax_type,
            "shipping_product_id": self.shipping_product_id.id

        }
        # print("aryanmaurya",vals)
        data = self.env["prestashop.instance"].create(vals)
        print("DATADATADATA+", data.name)


    def create_shops(self):
        active_id = self._context.get('active_id')
        presta_shop_obj = self.env['prestashop.shop']
        prestashop = presta_shop_obj.presta_connect()
        shops = prestashop.get('shops', 1)
        shop = ET.tostring(shops)

        tags = shops.tag

        for shop in shops.findall('./shop'):
            id = shop.find('id').text
            name = shop.find('name').text

        #         shop_config=prestashop.get('configurations',1)
        #         print 'shop_config',shop_config
        #         print  ET.tostring(shop_config)
        return name

    def _select_versions(self):
        """ Available versions
        Can be inherited to add custom versions.
        """
        return [('1.7', '1.7')]

    _sql_constraints = [
        ('name', 'unique (name)', 'The name already Exists!'), ]

    name = fields.Char('Name')
    version = fields.Selection(_select_versions, string='Version', required=True, default='1.7')
    location = fields.Char('Location', default='http://localhost/prestashop', required=True)
    cust_address = fields.Many2one('res.partner', 'Address', )
    webservice_key = fields.Char('Webservice key',
                                 help="You have to put it in 'username' of the PrestaShop ""Webservice api path invite",
                                 required=True)
    shipping_product_id = fields.Many2one('product.product', 'Shipping Product')

    tax_type = fields.Selection([('tax_include', 'Tax Include?'), ('tax_exclude', 'Tax Exclude?')],
                                string='Tax Consider in Odoo', default='tax_exclude')

    mapped_product_by = fields.Selection(
        [('presta_id', 'Prestashop Id'), ('default_code', 'Refrence'), ('barcode', 'Barcode')],
        string='Mapped Product By')

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse',
                                   help='Warehouse used to compute the stock quantities.')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_policy = fields.Selection([
        ('manual', 'On Demand'),
        ('picking', 'On Delivery Order'),
        ('prepaid', 'Before Delivery'),
    ], 'Create Invoice',
        help="""On demand: A draft invoice can be created from the sales order when needed. \nOn delivery order: A draft invoice can be created from the delivery order when the products have been delivered. \nBefore delivery: A draft invoice is created from the sales order and must be paid before the products can be delivered.""")
