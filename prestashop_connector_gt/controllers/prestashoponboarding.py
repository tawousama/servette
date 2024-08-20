# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class OnboardingController(http.Controller):

    @http.route('/presta/prestashop_onboarding_panel_custom', auth='user', type='json')
    def sale_quotation_onboarding_custom(self):
        current_company_id = []
        if request.httprequest.cookies.get('cids'):
            current_company_id = request.httprequest.cookies.get('cids').split(',')
        company = False
        if len(current_company_id) > 0 and current_company_id[0] and \
                current_company_id[0].isdigit():
            company = request.env['res.company'].sudo().search(
                [('id', '=', int(current_company_id[0]))])
        if not company:
            company = request.env.company
        # if not request.env.is_admin() or \
        #         company.magento_onboarding_state == 'closed':
            return {}
        # print('aaaaa')
        # company = request.env.company
        # print('company+++++', company)

        hide_panel = company.magento_onboarding_toggle_state != 'open'
        btn_value = 'Create more Prestashop instance' if hide_panel else 'Hide On boarding Panel'
        if not request.env.is_admin() or \
           company.sale_quotation_onboarding_state == 'closed':
            return {}
        #
        label = 'prestashop_connector_gt.sale_quotation_onboarding_panel_presta'
        return {
            'html': request.env.ref(label)._render({
                'company': company,
                'toggle_company_id': company.id,
                'hide_panel': hide_panel,
                'btn_value': btn_value,
                'state': company.get_and_update_sale_quotation_onboarding_state_custom(),
                # 'is_button_active': company.is_create_magento_more_instance

                # 'btn_value': btn_value,
            })
        }
