from odoo import models, fields, api
from random import choice



class ProducProduct(models.Model):

    _inherit = 'product.template'

    website_show_price = fields.Boolean( string='Website hide price')

