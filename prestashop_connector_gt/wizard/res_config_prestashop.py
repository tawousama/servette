# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
"""
Describes configuration for Magento Instance.
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigInstance(models.TransientModel):
    """
    Describes configuration for Prestashop instance
    """
    _name = 'res.config.instance'
    _description = 'Res Config Instance'

    instance_name = fields.Char("Instance Name")

    def create_instance(self):
        cr_inst = self.env['prestashop.instance'].search([('name', '=', self.name)])
        print('object++++++++++', cr_inst)
        if cr_inst:
            raise UserError(_('The instance already exists for the given name.'))

    @api.model
    def action_open_prestashop_instance(self):
        print('click function')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "prestashop_connector_gt.action_bigcommerce_connector_onboard")
        # action['res_id'] = self.env.company.id
        return action
