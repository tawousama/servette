# -*- coding: utf-8 -*-
from odoo import fields, models, api

MAGENTO_ONBOARDING_STATES = [
    ('not_done', "Not done"), ('just_done', "Just done"), ('done', "Done"), ('closed', "Closed")]


class ResCompany(models.Model):
    _inherit = "res.company"

    name = fields.Char(string="Name")

    sale_quotation_onboarding_state_custom = fields.Selection(
        [('not_done', "Not done"), ('just_done', "Just done"), ('done', "Done"), ('closed', "Closed")])
    bases_onboarding_company_state_custom = fields.Selection(
        selection=[('open', "Open"), ('closed', "Closed")], default='open')

    magento_onboarding_toggle_state = fields.Selection(
        selection=[('open', "Open"), ('closed', "Closed")], default='open')

    def get_and_update_sale_quotation_onboarding_state_custom(self):
        print('yessssssss', self)
        steps = [
            'bases_onboarding_company_state_custom',
            # 'account_onboarding_invoice_layout_state',
            # 'sale_onboarding_order_confirmation_state',
            # 'sale_onboarding_sample_quotation_state',
        ]
        return self.get_and_update_onbarding_state('sales_quotation_onboarding_state_custom', steps)

    @api.model
    def action_close_magento_instances_onboarding_panel(self):
        """ Mark the onboarding panel as closed. """
        self.env.company.sales_quotation_onboarding_state_custom = 'closed'

    # def get_and_update_prestashop_instances_onboarding_state(self):
    #     """ This method is called on the controller rendering method and ensures that the animations
    #         are displayed only one time. """
    #     steps = [
    #         'magento_instance_onboarding_state',
    #
    #     ]
    #     return self.get_and_update_onbarding_state('magento_onboarding_state', steps)

    # def action_toggle_magento_instances_onboarding_panel(self):
    #     """
    #     To change and pass the value of selection of current company to hide / show panel.
    #     :return Selection Value
    #     """
    #     self.bases_onboarding_company_state_custom = 'closed' if self.bases_onboarding_company_state_custom == 'open' else 'open'
    #     return self.bases_onboarding_company_state_custom
