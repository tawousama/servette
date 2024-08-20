# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
"""
Describes product import export process.
"""
import base64
import csv
import xlrd
import io
import os
from csv import DictWriter
from io import StringIO
from datetime import datetime, timedelta
from odoo.tools.misc import xlsxwriter
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class PrestashopImportExportEpt(models.TransientModel):
    """
    Describes Prestashop Process for import/ export operations
    """
    _name = 'gt.prestashop.import.export'
    _description = 'prestashop Import Export Gt'

    prestashops_instance_ids = fields.Many2many('prestashop.instance', string="Instances",
                                                help="This field relocates Prestashop Instance")
    # shop_ids = fields.Many2many('prestashop.shop', string="Select Shops")

    def action_import_wizard(self):
        id = self.env['prestashop.shop'].search([])
        if not len(id) > 1:
            vals = {
                "shop_ids": [(4, id.id)],

            }
        else:
            vals = {}
        wizard_id = self.env['prestashop.connector.wizard'].create(vals)
        return {
            'name': _('Operations'),
            'type': 'ir.actions.act_window',
            'res_model': 'prestashop.connector.wizard',
            'view_id': self.env.ref('prestashop_connector_gt.view_import_prestashop_connector_wizard_form_view').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard_id.id,
        }

    def action_update_wizard(self):
        id = self.env['prestashop.shop'].search([])
        if not len(id) > 1:
            vals = {
                "shop_ids": [(4, id.id)],

            }
        else:
            vals = {}
        wizard_id = self.env['prestashop.connector.wizard'].create(vals)
        return {
            'name': _('Operations'),
            'type': 'ir.actions.act_window',
            'res_model': 'prestashop.connector.wizard',
            'view_id': self.env.ref('prestashop_connector_gt.view_import_prestashop_connector_wizard_form_view').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard_id.id,
        }

    def action_export_wizard(self):
        id = self.env['prestashop.shop'].search([])
        if not len(id) > 1:
            vals = {
                "shop_ids": [(4, id.id)],

            }
        else:
            vals = {}

        wizard_id = self.env['prestashop.connector.wizard'].create(vals)
        return {
            'name': _('Operations'),
            'type': 'ir.actions.act_window',
            'res_model': 'prestashop.connector.wizard',
            'view_id': self.env.ref('prestashop_connector_gt.view_import_prestashop_connector_wizard_form_view').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard_id.id,
        }


