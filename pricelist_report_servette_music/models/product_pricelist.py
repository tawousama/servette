# -*- coding: utf-8 -*-

from odoo import fields, models


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    title_report_sm = fields.Char('Titre rapport Servette Music', translate=True)
