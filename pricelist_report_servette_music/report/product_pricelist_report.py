# -*- coding: utf-8 -*-

from odoo import api, models


class report_product_pricelist_sm(models.AbstractModel):
    _name = 'report.pricelist_report_servette_music.report_pricelist'
    _description = 'Rapport de liste de prix Servette Music'

    def _get_report_values(self, docids, data):

        product_ids = [int(i) for i in data['active_ids'].split(',')]
        pricelist_id = data['pricelist_id'] and int(data['pricelist_id']) or None
        with_ref = False if data['with_ref'] == 'false' else True
        return self._get_report_data(product_ids, pricelist_id, with_ref, 'pdf')

    @api.model
    def get_html(self):
        render_values = self._get_report_data(
            self.env.context.get('active_ids'),
            self.env.context.get('pricelist_id'),
            self.env.context.get('with_ref'),
        )
        return self.env['ir.qweb']._render('pricelist_report_servette_music.report_pricelist_page', render_values)

    def _get_report_data(self, active_ids, pricelist_id, with_ref, report_type='html'):
        products = []
        ProductClass = self.env['product.template']
        ProductPricelist = self.env['product.pricelist']
        pricelist = ProductPricelist.browse(pricelist_id)
        if not pricelist:
            pricelist = ProductPricelist.search([], limit=1)

        records = ProductClass.browse(active_ids) if active_ids else ProductClass.search([('sale_ok', '=', True)])
        for product in records:
            product_data = self._get_product_data(product, pricelist)

            products.append(product_data)

        return {
            'pricelist': pricelist,
            'products': products,
            'with_ref': with_ref,
            'is_html_type': report_type == 'html',
        }

    def _get_product_data(self, product, pricelist):
        data = {
            'id': product.id,
            'default_code': product.default_code,
            'name': product.name + ', ' + product.description_sale if product.description_sale else product.name,
            'price': pricelist._get_product_price(product, 1, False)
        }

        return data
