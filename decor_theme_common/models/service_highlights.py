# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductServices(models.Model):
    _name = "product.service"
    _description = "Product Services"


    name = fields.Char("Name", required=True)
    description = fields.Html("Description")
    visible_desc = fields.Boolean("Visible description in popup", default=True)
    

class ProductHighlights(models.Model):
    _name = "product.highlights"
    _description = "Product Highlights"


    name = fields.Char("Highlight Text")
