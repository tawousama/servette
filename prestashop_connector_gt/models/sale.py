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
from odoo.exceptions import UserError, ValidationError
import socket
from datetime import timedelta, datetime, date, time
import time
from odoo import netsvc
from odoo.tools.translate import _
import urllib
import base64
from operator import itemgetter
from itertools import groupby
#
import logging
import cgi
import odoo.addons.decimal_precision as dp
from odoo.addons.prestashop_connector_gt.prestapyt.prestapyt import PrestaShopWebService as PrestaShopWebService
from odoo.addons.prestashop_connector_gt.prestapyt.prestapyt import PrestaShopWebServiceDict as PrestaShopWebServiceDict


class sale_order(models.Model):
    _inherit = "sale.order"

    prestashops_order = fields.Boolean('Prestashops Order')
    shop_id = fields.Many2one('prestashop.shop', 'Shop ID')
    prestaa_instance_id = fields.Many2one("prestashop.instance", "Prstashop Instance Id")
    presta_order_date = fields.Datetime(string="Presta Date")
    order_status = fields.Many2one('presta.order.status', string="Status")
    presta_order_ref = fields.Char('Order Reference')
    pretsa_payment_mode = fields.Selection(
        [('bankwire', 'Bankwire'), ('cheque', 'Payment By Cheque'), ('banktran', 'Bank transfer'),
         ('cod', 'Cash on delivery  (COD)')], string='Payment mode', default='cheque')
    carrier_prestashop = fields.Many2one('delivery.carrier', string='Carrier In Prestashop')
    workflow_order_id = fields.Many2one('import.order.workflow', string='Order Work Flow')
    prestashop_order = fields.Boolean('Prestashop Order')
    message_order_ids = fields.One2many('order.message', 'new_id', 'Message Info')
    token = fields.Char('Token')
    presta_id = fields.Char('presta_id')
    shop_ids = fields.Many2many('prestashop.shop', 'saleorder_shop_rel', 'saleorder_id', 'shop_id', string="Shop")
    write_date = fields.Datetime(string="Write Date")
    to_be_exported = fields.Boolean(string="To be exported?")
    order_status_update = fields.Boolean(string="To Update Order Status")

    def action_update_order_status(self):
        sale_order = self.env['sale.order']
        status_obj = self.env['presta.order.status']
        for shop in self:
            prestashop = PrestaShopWebServiceDict(shop.shop_id.shop_physical_url,
                                                  shop.shop_id.prestashop_instance_id.webservice_key or None)
            sale_order_ids = sale_order.search([('order_status_update', '=', True)])
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


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    gift = fields.Boolean('Gift')
    gift_message = fields.Char('Gift Message')
    wrapping_cost = fields.Float('Wrapping Cost')
    presta_id = fields.Char('presta_id')
    presta_line = fields.Boolean('Is Presta line')

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state', 'order_id.workflow_order_id')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:

            if line.order_id.state in ['sale', 'done']:
                if not line.order_id.workflow_order_id:
                    if line.product_id.invoice_policy == 'order':
                        line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                    else:
                        line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
                else:
                    if line.order_id.workflow_order_id.invoice_policy == 'order':
                        line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                    elif line.order_id.workflow_order_id.invoice_policy == 'delivery':
                        line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0


class prestaOrderStatus(models.Model):
    _name = 'presta.order.status'
    _description = 'Prestashop Order Status'

    name = fields.Char(string="Status")
    presta_id = fields.Char(string="Presta ID")
    confirm_order = fields.Boolean(string="Order Confirm")
    shipped = fields.Boolean(string="Shipped")
    paid = fields.Boolean(string="Paid")

    @api.onchange('confirm_order', 'shipped', 'paid')
    def selection_onchange(self):
        if self.confirm_order == True:
            if self.shipped:
                raise UserError(_('You can select one order status at a time'))
            elif self.paid:
                raise UserError(_('You can select one order status at a time'))
        elif self.paid == True:
            if self.confirm_order:
                raise UserError(_('You can select one order status at a time'))
            elif self.shipped:
                raise UserError(_('You can select one order status at a time'))
        elif self.shipped == True:
            if self.confirm_order:
                raise UserError(_('You can select one order status at a time'))
            elif self.paid:
                raise UserError(_('You can select one order status at a time'))
