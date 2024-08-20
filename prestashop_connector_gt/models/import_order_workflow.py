 
from odoo import api, fields, models, _


class ImportOrderWorkflow(models.Model):
    _name = "import.order.workflow"
    _description = 'Import Order Worklow'

    name = fields.Char(string="Name")
    validate_order = fields.Boolean(string="Validate Order")
    create_invoice = fields.Boolean(string="Create Invoice")
    validate_invoice = fields.Boolean(string="Validate Invoice")
    register_payment = fields.Boolean(string="Register Payment")
    complete_shipment = fields.Boolean(string="Complete Shipment")
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities')],
        string='Invoicing Policy', default='order')
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, readonly=True, default='direct')