import json
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from odoo.exceptions import Warning
import time


class PrestashopShop(models.Model):
    _inherit = 'prestashop.shop'
    _description = "The prestashop determines the prestashop view"
    # _order = 'sequence'

    # presta_kanban_dashboard = fields.Text(compute='_presta_kanban_dashboard')
    color = fields.Integer(string='Color Index')
    # prestashop_instance_ids = fields.Many2one('prestashop.instance', string='Prestashop Instance')
    prestashop_store_view_ids = fields.Many2one(comodel_name="prestashop.shop",
                                                string='Prestashop Store Views')


    presta_website_id = fields.Char(string="Prestashop Website", help="Prestashop Website Id")

    website_display_currency = fields.Many2one(comodel_name="res.currency", readonly=True,
                                               help="Display currency of the magento website.")

    prestashop_order_data = fields.Text(compute="_compute_kanban_prestashop_order_data")

    def show_prestashop_instance(self):
        """
        Use: To prepare Magento Instance action
        :return: Magento Instance action details
        """
        view_ref = self.env.ref('prestashop_connector_gt.prestashop_instance_form_view').ids
        print("view_ref+_+_+_+1", view_ref)
        view_id = view_ref if view_ref else False
        print("view_id+_+_+_+_+", view_id)
        return {
            'name': _('Prestashop Instance'),
            'res_model': 'prestashop.instance',
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': self.prestashop_instance_id.id,
            'target': 'current'
        }

    def show_prestashop_store(self):
        view_ref = self.env.ref('prestashop_connector_gt.prestaerp_view_shop_form').ids
        print("view_ref+_+_+_+1", view_ref)
        view_id = view_ref if view_ref else False
        print("view_id+_+_+_+_+", view_id)
        return {
            'name': _('Prestashop Shop'),
            'res_model': 'prestashop.shop',
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': self.id,
            'target': 'current'
        }

    @staticmethod
    def prepare_action(view, domain):
        print('syhduuuuufwuiegfiuwegfuie', view)
        print('syhduuuuufwuiegfiuwegfuie', view.get('views'))
        """
        Use: To prepare action dictionary
        :return: action details
        """
        action_dic = {
            'name': view.get('name'),
            'domain': domain,
            'type': view.get('type'),
            'view_id': view.get('view_id')[0] if view.get('view_id') else False,
            'view_mode': view.get('view_mode'),
            'res_model': view.get('res_model'),
            'views': view.get('views'),
            'target': view.get('target'),
        }
        if 'tree' in action_dic['views'][0]:
            action_dic['views'][0] = (action_dic['view_id'], 'list')
        return action_dic

    def get_total_products(self, record, exported, product_type=False):
        """
        Use: To get the list of products exported from Magento website
        Here if exported = True, then only get those record which having sync_product_with_magento= true
        if exported = False, then only get those record which having sync_product_with_magento= false
        if exported = All, then get all those records which having sync_product_with_magento = true and false
        :param product_type: magento product type
        :param record: magento website object
        :param exported: exported is one of the "True" or "False" or "All"
        :return: total number of Magento products ids and action for products
        """
        product_data = {}
        product_domain = []
        product_domain.append(('prestashop_product_template_id', '=', self.prestashop_instance_id.id))
        product_count = self.env['product.template'].search(product_domain)
        if exported:
            product_domain.append(('prestashop_product', '=', True))
        elif exported:
            product_domain.append(('prestashop_product', '=', False))
        elif exported == '':
            print('Hurray')
        result = self.env['product.template'].search(product_domain)
        total_count = 0
        if result:
            total_count = len(result)
        view = self.env.ref('prestashop_connector_gt.inherit_product_template_action').sudo().read()[
            0]
        action = record.prepare_action(view, product_domain)
        product_data.update({'product_count': total_count, 'product_action': action})
        return product_data

    def gt_prestashop_product_exported(self):
        """
        get exported as true product action
        :return:
        """
        exported = False
        exported_product_data = self.get_total_products(self, exported)
        return exported_product_data.get('product_action')

    def gt_prestashop_product_not_exported(self):
        """
        get not export prestashop products
        :return:
        """
        exported = True
        exported_product_data = self.get_total_products(self, exported)
        return exported_product_data.get('product_action')

    def gt_prestashop_product_all_exported(self):
        """
        get all prestashop product
        :return:
        """
        exported = ''
        exported_product_data = self.get_total_products(self, exported)
        return exported_product_data.get('product_action')

    def gt_magento_action_sales_quotations(self):
        """
        get quotations action
        :return:
        """
        state = ('draft', 'sent')
        order_quotation_data = self.get_total_orders(self, state)
        return order_quotation_data.get('product_action')

    def gt_magento_action_sales_order(self):
        """
        get quotations action
        :return:
        """
        state = 'sale'
        order_quotation_data = self.get_total_orders(self, state)
        return order_quotation_data.get('product_action')

    def get_total_orders(self, record, product_type=False):
        """
        Use: To get the list of products exported from Magento website
        Here if exported = True, then only get those record which having sync_product_with_magento= true
        if exported = False, then only get those record which having sync_product_with_magento= false
        if exported = All, then get all those records which having sync_product_with_magento = true and false
        :param product_type: magento product type
        :param record: magento website object
        :param exported: exported is one of the "True" or "False" or "All"
        :return: total number of Magento products ids and action for products
        """
        quotation_data = {}
        quotation_domain = []
        quotation_domain.append(('shop_id', '=', self.prestashop_instance_id.id))
        result = self.env['sale.order'].search(quotation_domain)
        print("RESULTTT+_+_+_+_+_++_++_++_+_++__+_+____+_++", result)

        total_count = 0
        if result:
            total_count = len(result)
        view = self.env.ref('prestashop_connector_gt.inherit_action_quotations').sudo().read()[
            0]
        print("VIEWVIEW_+_+_+_+_+_+_+_+_+_+_+_++_+_+_+_+_", view)
        order_action = record.prepare_action(view, quotation_domain)
        quotation_data.update(
            {'order_count': total_count, 'product_action': order_action})
        print("DATAUPDATE__+_+_+_+_+_+_+_+_+_+_+_+_+", quotation_data)
        return quotation_data

    def get_prestashop_picking_records(self, record, product_type=False):
        quotation_data = {}
        stock_domain = []
        stock_domain.append(('shop_ids', '=', self.id))
        print("ASDFGHJKLWERTYUUI+_+_+_+_+_+_+_+_+_+_+_+", stock_domain)
        result = self.env['stock.picking'].search(stock_domain)
        print("RESULTTT+_+_+_+_+_++_++_++_+_++__+_+____+_++", result)

        total_count = 0
        if result:
            total_count = len(result)
        print("TOTALCOUNTTOTAL_++_+_+_+_+_+__+_+_+", total_count)
        view = self.env.ref('prestashop_connector_gt.inherit_action_picking_tree_all').sudo().read()[
            0]
        # data = self.env.ref('prestashop_connector_gt.inherit_action_orders').sudo().read()[
        #     0]
        print("VIEWVIEW_+_+_+_+_+_+_+_+_+_+_+_++_+_+_+_+_", view)
        print('RECORD+_+_+_+_+_+_+_+_', record)
        order_action = record.prepare_action(view, stock_domain)
        # sales_order_actions = record.prepare_action(data, quotation_domain)
        quotation_data.update(
            {'order_count': total_count, 'product_action': order_action})
        print("DATAUPDATE__+_+_+_+_+_+_+_+_+_+_+_+_+", quotation_data)
        return quotation_data

    def gt_prestashop_waiting_stock_picking(self):
        """
        get confirmed state picking action
        :return:
        """
        state = 'confirmed'
        confirmed_picking_data = self.get_prestashop_picking_records(self, state)
        return confirmed_picking_data.get('product_action')

    def gt_prestashop_waiting_available_stock_picking(self):
        """
        get partially_available state picking action
        :return:
        """
        state = 'partially_available'
        picking_data = self.get_prestashop_picking_records(self, state)
        return picking_data.get('product_action')

    def gt_ready_stock_picking(self):
        """
        get assigned state picking action
        :return:
        """
        state = 'assigned'
        picking_data = self.get_prestashop_picking_records(self, state)
        return picking_data.get('product_action')

    def gt_transferred_stock_picking(self):
        """
        get done state picking action
        :return:
        """
        state = 'done'
        picking_data = self.get_prestashop_picking_records(self, state)
        return picking_data.get('product_action')

    # INVOIVEEEEE

    def gt_invoice_invoices_open(self):
        """
        get draft state invoice action
        :return:
        """
        state = 'draft'
        invoice_data = self.invoice_invoices_open_gt(self, state)
        return invoice_data.get('product_action')

    def gt_invoice_invoices_paid(self):
        """
        get posted state invoice action
        :return:
        """
        state = 'posted'
        invoice_data = self.invoice_invoices_open_gt(self, state)
        return invoice_data.get('product_action')

    def invoice_invoices_open_gt(self, record, product_type=False):
        quotation_data = {}
        stock_domain = []
        stock_domain.append(('shop_ids', '=', self.id))
        print("ASDFGHJKLWERTYUUIfgggggggggggggd+_+_+_+_+_+_+_+_+_+_+_+", stock_domain)
        result = self.env['account.move'].search(stock_domain)
        print("RESULTTT+_+_+_+_+_++_++_++_+_++__+_+____+_++", result)

        total_count = 0
        if result:
            total_count = len(result)
        # print("TOTALCOUNT_+_+++++++++++++++++++++++", total_count)
        view = self.env.ref('prestashop_connector_gt.inherit_action_invoice_tree1').sudo().read()[
            0]
        # data = self.env.ref('prestashop_connector_gt.inherit_action_orders').sudo().read()[
        #     0]
        # print("VIEWVIEW_+_+_+_+_+_+_+_+_+_+_+_++_+_+_+_+_", view)
        print('RECORD+_+_+_+_+_+_+_+_', record)
        order_action = record.prepare_action(stock_domain)
        # sales_order_actions = record.prepare_action(data, quotation_domain)
        quotation_data.update(
            {'order_count': total_count, 'product_action': order_action})
        print("DATAUPDATE__+_+_+_+_+_+_+_+_+_+_+_+_+", quotation_data)
        return quotation_data

    def _compute_kanban_prestashop_order_data(self):
        if not self._context.get('sort'):
            print("self._context.get+_+_+_+_+_",self._context.get)
            context = dict(self.env.context)
            print("CONTEXT+_+_+_+_+_+_+_+_+_+_+_+_+__+", context)
            context.update({'sort': 'week'})
            print('CONTEXTUPDATE+_+_+_+_+_+_+_+_+_+', context)
            self.env.context = context
            print("SELFENVCPNTET_+_+_+_+_+_+_+", self)
        for record in self:
            # Prepare values for Graph website vise
            values = record.get_graph_data(record)
            data_type, comparison_value = record.get_compare_data(record)
            # Total sales website vise
            total_sales = round(sum([key['y'] for key in values]), 2)
            # Product count website vise query
            # exported = 'All'
            # product_data = record.get_total_products(record, exported)
            # Customer count website vise query
            # customer_data = record.get_customers(record)
            # Order count website vise query
            order_data = record.get_total_orders(record)
            # Order shipped website vise count query
            # order_shipped = record.get_shipped_orders(record)
            # refund count query
            # refund_data = self.env['prestashop.instance'].get_refund(record)
            print('order_data+++++++++++++', order_data)
            record.prestashop_order_data = json.dumps({
                "title": "",
                "values": values,
                "area": True,
                "key": "Order: Untaxed amount",
                "color": "#875A7B",
                # "total_sales": total_sales,
                "is_sample_data": False,
                "order_data": order_data,
                # "customer_data": customer_data,
                # "refund_data": refund_data,
                # "product_date": product_data,
                # "sort_on": self._context.get('sort'),
                # "order_shipped": order_shipped,
                "graph_sale_percentage": {'type': data_type, 'value': comparison_value},
                "currency_symbol": self.pricelist_id.currency_id.symbol or '',
                # remove currency symbol same as odoo
            })

    def get_graph_data(self, record):
        """
        Use: To get the details of Magento sale orders and total amount month wise or year wise to prepare the graph
        :return: Magento sale order date or month and sum of sale orders amount of current instance
        """

        def get_current_week_date(record):
            print("GETCURRENTWEEKDATA+_+_+_+_+_+_+_+", record)
            self._cr.execute("""SELECT to_char(date(d.day),'DAY'), t.amount_untaxed as sum
                                FROM  (
                                   SELECT day
                                   FROM generate_series(date(date_trunc('week', (current_date)))
                                    , date(date_trunc('week', (current_date)) + interval '6 days')
                                    , interval  '1 day') day
                                   ) d
                                LEFT   JOIN
                                (SELECT date(date_order)::date AS day, sum(amount_untaxed) as amount_untaxed
                                   FROM   sale_order
                                   WHERE  date(date_order) >= (select date_trunc('week', date(current_date)))
                                   AND    date(date_order) <= (select date_trunc('week', date(current_date))
                                   + interval '6 days')
                                   AND shop_id=%s and state in ('sale','done')
                                   GROUP  BY 1
                                   ) t USING (day)
                                ORDER  BY day""", ([record.id]))

            print("PRESTASHOPPPPPPPP+_+_+_+_+_+_+", record)
            datas = self._cr.dictfetchall()
            print("DATAS+_+_+_+_+_+_+_+_+_+_+_", datas)
            return datas

        def graph_of_current_month(record):
            self._cr.execute("""select EXTRACT(DAY from date(date_day)) :: integer,sum(amount_untaxed) from (
                        SELECT
                          day::date as date_day,
                          0 as amount_untaxed
                        FROM generate_series(date(date_trunc('month', (current_date)))
                            , date(date_trunc('month', (current_date)) + interval '1 MONTH - 1 day')
                            , interval  '1 day') day
                        union all
                        SELECT date(date_order)::date AS date_day,
                        sum(amount_untaxed) as amount_untaxed
                          FROM   sale_order
                        WHERE  date(date_order) >= (select date_trunc('month', date(current_date)))
                        AND date(date_order)::date <= (select date_trunc('month', date(current_date))
                        + '1 MONTH - 1 day')
                        and shop_id = %s and state in ('sale','done')
                        group by 1
                        )foo
                        GROUP  BY 1
                        ORDER  BY 1""", ([record.id]))
            return self._cr.dictfetchall()

        #
        def graph_of_current_year(record):
            self._cr.execute("""select TRIM(TO_CHAR(DATE_TRUNC('month',month),'MONTH')),sum(amount_untaxed) from
                                (SELECT DATE_TRUNC('month',date(day)) as month,
                                  0 as amount_untaxed
                                FROM generate_series(date(date_trunc('year', (current_date)))
                                , date(date_trunc('year', (current_date)) + interval '1 YEAR - 1 day')
                                , interval  '1 MONTH') day
                                union all
                                SELECT DATE_TRUNC('month',date(date_order)) as month,
                                sum(amount_untaxed) as amount_untaxed
                                  FROM   sale_order
                                WHERE  date(date_order) >= (select date_trunc('year', date(current_date))) AND
                                date(date_order)::date <= (select date_trunc('year', date(current_date))
                                + '1 YEAR - 1 day')
                                and shop_id = %s and state in ('sale','done')
                                group by DATE_TRUNC('month',date(date_order))
                                order by month
                                )foo
                                GROUP  BY foo.month
                                order by foo.month""", ([record.id]))
            return self._cr.dictfetchall()

        # def graph_of_all_time(record):
        #     self._cr.execute("""select TRIM(TO_CHAR(DATE_TRUNC('month',date_order),'YYYY-MM')),sum(amount_untaxed)
        #                         from sale_order where magento_instance_id = %s and state in ('sale','done')
        #                         and shop_id = %s
        #                         group by DATE_TRUNC('month',date_order)
        #                         order by DATE_TRUNC('month',date_order)""", ([record.id]))
        #     return self._cr.dictfetchall()

        # Prepare values for Graph
        values = []
        if self._context.get('sort') == 'week':
            website_vise_result = get_current_week_date(record)
        elif self._context.get('sort') == "month":
            website_vise_result = graph_of_current_month(record)
        elif self._context.get('sort') == "year":
            website_vise_result = graph_of_current_year(record)
        # else:
        #     website_vise_result = graph_of_all_time(record)
        if website_vise_result:
            for data in website_vise_result:
                values.append({"x": ("{}".format(data.get(list(data.keys())[0]))),
                               "y": data.get('sum') or 0.0})
        return values

    def get_compare_data(self, record):
        """
        :param record: Magento instance
        :return: Comparison ratio of orders (weekly,monthly and yearly based on selection)
        """
        data_type = False
        total_percentage = 0.0

        if self._context.get('sort') == 'week':
            website_current_total, website_previous_total = self.get_compared_week_data(record)
        elif self._context.get('sort') == "month":
            website_current_total, website_previous_total = self.get_compared_month_data(record)
        elif self._context.get('sort') == "year":
            website_current_total, website_previous_total = self.get_compared_year_data(record)
        # else:
        #     website_current_total, website_previous_total = 0.0, 0.0
        if website_current_total > 0.0:
            if website_current_total >= website_previous_total:
                data_type = 'positive'
                total_percentage = (
                                           website_current_total - website_previous_total) * 100 / website_current_total
            if website_previous_total > website_current_total:
                data_type = 'negative'
                total_percentage = (
                                           website_previous_total - website_current_total) * 100 / website_current_total
        return data_type, round(total_percentage, 2)

    def get_compared_week_data(self, record):
        website_current_total = 0.0
        website_previous_total = 0.0
        day_of_week = date.weekday(date.today())
        self._cr.execute("""select sum(amount_untaxed) as current_week from sale_order
                               where date(date_order) >= (select date_trunc('week', date(current_date))) and
                               shop_id=%s and state in ('sale','done')""",
                         ([record.id]))
        current_week_data = self._cr.dictfetchone()
        if current_week_data and current_week_data.get('current_week'):
            website_current_total = current_week_data.get('current_week')
        # Previous week data
        self._cr.execute("""select sum(amount_untaxed) as previous_week from sale_order
                           where date(date_order) between (select date_trunc('week', current_date) - interval '7 day')
                           and (select date_trunc('week', (select date_trunc('week', current_date) - interval '7
                           day')) + interval '%s day')
                           and shop_id=%s and state in ('sale','done')
                           """, ([day_of_week, record.id]))
        previous_week_data = self._cr.dictfetchone()
        if previous_week_data and previous_week_data.get('previous_week'):
            website_previous_total = previous_week_data.get('previous_week')
        return website_current_total, website_previous_total

    def get_compared_month_data(self, record):
        website_current_total = 0.0
        website_previous_total = 0.0
        day_of_month = date.today().day - 1
        self._cr.execute("""select sum(amount_untaxed) as current_month from sale_order
                               where date(date_order) >= (select date_trunc('month', date(current_date)))
                               and shop_id=%s and state in ('sale','done')""",
                         ([record.id]))
        current_data = self._cr.dictfetchone()
        if current_data and current_data.get('current_month'):
            website_current_total = current_data.get('current_month')
        # Previous week data
        self._cr.execute("""select sum(amount_untaxed) as previous_month from sale_order where date(date_order)
                           between (select date_trunc('month', current_date) - interval '1 month') and
                           (select date_trunc('month', (select date_trunc('month', current_date) - interval
                           '1 month')) + interval '%s days')
                           and shop_id=%s and state in ('sale','done')
                           """, ([day_of_month, record.id]))
        previous_data = self._cr.dictfetchone()
        if previous_data and previous_data.get('previous_month'):
            website_previous_total = previous_data.get('previous_month')
        return website_current_total, website_previous_total

    def get_compared_year_data(self, record):
        website_current_total = 0.0
        website_previous_total = 0.0
        year_begin = date.today().replace(month=1, day=1)
        year_end = date.today()
        delta = (year_end - year_begin).days - 1
        self._cr.execute("""select sum(amount_untaxed) as current_year from sale_order
                               where date(date_order) >= (select date_trunc('year', date(current_date)))
                               and shop_id=%s and state in ('sale','done')""",
                         ([record.id]))
        current_data = self._cr.dictfetchone()
        if current_data and current_data.get('current_year'):
            website_current_total = current_data.get('current_year')
        # Previous week data
        self._cr.execute("""select sum(amount_untaxed) as previous_year from sale_order where date(date_order)
                           between (select date_trunc('year', date(current_date) - interval '1 year')) and
                           (select date_trunc('year', date(current_date) - interval '1 year') + interval '%s days')
                           and shop_id=%s and state in ('sale','done')
                           """, ([delta, record.id]))
        previous_data = self._cr.dictfetchone()
        if previous_data and previous_data.get('previous_year'):
            website_previous_total = previous_data.get('previous_year')
        return website_current_total, website_previous_total

    # def get_draft_refund(self):
    #     context = self.env.context
    #     state = f"('{context.get('state')}')"
    #     result = self.env['prestashop.instance'].get_refund(self.prestashop_instance_id, self.id, state)
    #     return result.get('refund_action')
    #
    # def get_posted_refund(self):
    #     context = self.env.context
    #     state = f"('{context.get('state')}')"
    #     result = self.env['prestashop.instance'].get_refund(self.prestashop_instance_id, self.id, state)
    #     return result.get('refund_action')
    #
    # def get_cancelled_refund(self):
    #     context = self.env.context
    #     state = f"('{context.get('state')}')"
    #     result = self.env['prestashop.instance'].get_refund(self.prestashop_instance_id, self.id, state)
    #     return result.get('refund_action')

    # def get_customers(self, record):
    #     """
    #     Use: To get the list of customers with Magento instance for current Magento instance
    #     :return: total number of customer ids and action for customers
    #     """
    #     customer_data = {}
    #     main_sql = """select DISTINCT(rp.id) as partner_id from res_partner as rp
    #                     inner join magento_res_partner_ept mp on mp.partner_id = rp.id
    #                     where mp.shop_id=%s
    #                     """, ([record.id])
    #
    #     view = self.env.ref('base.action_partner_form').sudo().read()[0]
    #     self._cr.execute(main_sql)
    #     result = self._cr.dictfetchall()
    #     prestashop_customer_ids = []
    #     if result:
    #         for data in result:
    #             prestashop_customer_ids.append(data.get('partner_id'))
    #     action = record.prepare_action(view, [('id', 'in', prestashop_customer_ids)])
    #     customer_data.update(
    #         {'customer_count': len(prestashop_customer_ids), 'customer_action': action})
    #     return customer_data

    #
    # @api.model
    # def _presta_kanban_dashboard(self):
    #     order_obj = self.env['sale.order']
    #     invoice_obj = self.env['account.move']
    #     stock_obj = self.env['stock.picking']
    #
    #     all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
    #     pending_order_ids = order_obj.search(
    #         [('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', 'in', ('sale', 'sent'))])
    #     complete_order_ids = order_obj.search(
    #         [('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', '=', 'done')])
    #     draft_order_ids = order_obj.search(
    #         [('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', '=', 'draft')])
    #     cancel_order_ids = order_obj.search(
    #         [('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', '=', 'cancel')])
    #     #
    #     origin_list = [s.name for s in all_order_ids]
    #     all_invoice_ids = invoice_obj.search([('is_prestashop', '=', True), ('invoice_origin', 'in', origin_list)])
    #     pending_invoice_ids = invoice_obj.search(
    #         [('is_prestashop', '=', True), ('invoice_origin', 'in', origin_list), ('state', '!=', 'paid')])
    #     complete_invoice_ids = invoice_obj.search(
    #         [('is_prestashop', '=', True), ('invoice_origin', 'in', origin_list), ('state', '=', 'paid')])
    #     draft_invoice_ids = invoice_obj.search(
    #         [('is_prestashop', '=', True), ('invoice_origin', 'in', origin_list), ('state', '=', 'draft')])
    #     cancel_invoice_ids = invoice_obj.search(
    #         [('is_prestashop', '=', True), ('invoice_origin', 'in', origin_list), ('state', '=', 'cancel')])
    #
    #     all_stock_ids = stock_obj.search([('is_presta', '=', True), ('origin', 'in', origin_list)])
    #     pending_stock_ids = stock_obj.search(
    #         [('is_presta', '=', True), ('origin', 'in', origin_list), ('state', 'in', ('confirmed', 'waiting'))])
    #     complete_stock_ids = stock_obj.search(
    #         [('is_presta', '=', True), ('origin', 'in', origin_list), ('state', '=', 'done')])
    #     #         late_delivey_ids = stock_obj.search([('is_presta','=',True),('origin', 'in', origin_list),('min_date','<',datetime.today())])
    #     back_order_ids = stock_obj.search(
    #         [('is_presta', '=', True), ('origin', 'in', origin_list), ('backorder_id', '<>', False)])
    #
    #     prestashop_webservices = {
    #
    #         'all_order': len(all_order_ids),
    #         'pending_order': len(pending_order_ids),
    #         'complete_order': len(complete_order_ids),
    #         'draft_order': len(draft_order_ids),
    #         'cancel_order': len(cancel_order_ids),
    #
    #         'all_invoice': len(all_invoice_ids),
    #         'pending_invoice': len(pending_invoice_ids),
    #         'complete_invoice': len(complete_invoice_ids),
    #         'draft_invoice': len(draft_invoice_ids),
    #         'cancel_invoice': len(cancel_invoice_ids),
    #
    #         'all_stock': len(all_stock_ids),
    #         'pending_stock': len(pending_stock_ids),
    #         'complete_stock': len(complete_stock_ids),
    #         #         'late_delivey':late_delivey_ids,
    #         'back_order': len(back_order_ids),
    #
    #     }
    #     self.presta_kanban_dashboard = json.dumps(prestashop_webservices)

    # @api.multi
    def action_view_all_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id', '=', self[0].id)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        #         elif len(order_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_draft_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', '=', 'draft')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        #         elif len(order_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_cancel_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search(
            [('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', '=', 'cancel')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        #         elif len(order_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_pending_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search(
            [('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', 'in', ('sale', 'sent'))])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        #         elif len(order_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_complete_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id', '=', self[0].id), ('presta_id', '!=', False), ('state', '=', 'done')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        #         elif len(order_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_all_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.move']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search([('is_prestashop', '=', True), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_view_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.view_move_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        #         elif len(invoice_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = invoice_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_pending_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.move']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_prestashop', '=', True), ('state', '=', 'open'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_view_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.view_move_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        #         elif len(invoice_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = invoice_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_draft_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.move']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_prestashop', '=', True), ('state', '=', 'draft'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_view_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.view_move_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        #         elif len(invoice_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = invoice_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_cancel_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.move']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_prestashop', '=', True), ('state', '=', 'cancel'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_view_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.view_move_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        #         elif len(invoice_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = invoice_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_complete_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.move']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_prestashop', '=', True), ('state', '=', 'paid'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_view_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.view_move_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        #         elif len(invoice_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = invoice_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_all_stock(self):
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        stock_id = stock_obj.search([('is_presta', '=', True), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_all')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_id) > 1:
            result['domain'] = "[('id','in',%s)]" % stock_id.ids
        elif len(stock_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = stock_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_pending_stock(self):
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        stock_id = stock_obj.search(
            [('is_presta', '=', True), ('origin', 'in', origin_list), ('state', 'in', ('confirmed', 'waiting'))])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_all')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % stock_id.ids
        #         elif len(stock_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = stock_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    def action_view_complete_stock(self):
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        stock_id = stock_obj.search([('is_presta', '=', True), ('origin', 'in', origin_list), ('state', '=', 'done')])

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_all')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % stock_id.ids
        #         elif len(stock_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = stock_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    #     @api.multi
    #     def presta_action_picking_tree_late(self):
    #
    #
    #         shop_obj = self.env['prestashop.shop']
    #         order_obj =self.env['sale.order']
    #         stock_obj = self.env['stock.picking']
    #         shop_id  = shop_obj.search([('prestashop_instance_id','=',self.id)])
    #         all_order_ids = order_obj.search([('shop_id','=',shop_id.id)])
    #         origin_list = [s.name for s in all_order_ids]
    #         all_stock_ids = stock_obj.search([('is_presta','=',True), ('origin', 'in', origin_list)])
    #
    #         imd = self.env['ir.model.data']
    #         action = imd.xmlid_to_object('stock.action_picking_tree_late')
    #         list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
    #         form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
    #         result = {
    #             'name': action.name,
    #             'help': action.help,
    #             'type': action.type,
    #             'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
    #             'target': action.target,
    #             'context':{'search_default_late':1,'search_default_confirmed':1},
    #             'res_model': action.res_model,
    #         }
    #         print "result", result
    #         if len(all_stock_ids) >= 1:
    #             result['domain'] = "[('id','in',%s)]" % all_stock_ids.ids
    # #         elif len(stock_id) == 1:
    # #             result['views'] = [(form_view_id, 'form')]
    # #             result['res_id'] = stock_id.ids[0]
    #         else:
    #             result = {'type': 'ir.actions.act_window_close'}
    #         return result

    #     @api.multi
    #     def presta_action_picking_tree_backorder(self):
    #         shop_obj = self.env['prestashop.shop']
    #         order_obj =self.env['sale.order']
    #         stock_obj = self.env['stock.picking']
    #         shop_id  = shop_obj.search([('prestashop_instance_id','=',self.id)])
    #         all_order_ids = order_obj.search([('shop_id','=',shop_id.id)])
    #         origin_list = [s.name for s in all_order_ids]
    #         all_stock_ids = stock_obj.search([('is_presta','=',True), ('origin', 'in', origin_list)])
    #
    #         imd = self.env['ir.model.data']
    #         action = imd.xmlid_to_object('stock.action_picking_tree_backorder')
    #         list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
    #         form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
    #         result = {
    #             'name': action.name,
    #             'help': action.help,
    #             'type': action.type,
    #             'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
    #             'target': action.target,
    #             'context':{'search_default_backorder': 1,'search_default_confirmed': 1},
    #             'res_model': action.res_model,
    #         }
    #         print "result", result
    #         if len(all_stock_ids) >= 1:
    #             result['domain'] = "[('id','in',%s)]" % all_stock_ids.ids
    # #         elif len(stock_id) == 1:
    # #             result['views'] = [(form_view_id, 'form')]
    # #             result['res_id'] = stock_id.ids[0]
    #         else:
    #             result = {'type': 'ir.actions.act_window_close'}
    #         return result

    # @api.multi
    def presta_action_picking_tree_waiting(self):
        shop_obj = self.env['prestashop.shop']
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        shop_id = shop_obj.search([('prestashop_instance_id', '=', self.id)])
        all_order_ids = order_obj.search([('shop_id', '=', shop_id.id)])
        origin_list = [s.name for s in all_order_ids]
        all_stock_ids = stock_obj.search([('is_presta', '=', True), ('origin', 'in', origin_list)])

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_waiting')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': {'search_default_waiting': 1, },
            'res_model': action.res_model,
        }
        if len(all_stock_ids) >= 1:
            result['domain'] = "[('id','in',%s)]" % all_stock_ids.ids
        #         elif len(stock_id) == 1:
        #             result['views'] = [(form_view_id, 'form')]
        #             result['res_id'] = stock_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
