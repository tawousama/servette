# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.addons.website_sale.controllers import main


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _rec_name = "display_name"

    @api.depends("name", "parent_id", "parent_id.name")
    def _get_display_name(self):
        for obj in self:
            display_name = obj.name
            parent_id = obj.parent_id
            while parent_id:
                display_name = parent_id.name + " / " + display_name
                parent_id = parent_id.parent_id
            obj.display_name = display_name

    def get_product_brand_count(self):
        for obj in self:
            domain = [('brand_id', '=', obj.id)]
            if not obj.env.user.has_group('base.group_system'):
                domain.append(("website_published", '=', True))
            ctx = self.env.context or {}
            if 'product_brand_search' in ctx and ctx['product_brand_search']:
                domain.append(("name", 'ilike', ctx['product_brand_search'].strip()))
            product_template = self.env['product.template'].search(domain)
            obj.brand_count = len(product_template.ids)

    name = fields.Char("Name")
    brand_decription = fields.Text("Description")
    parent_id = fields.Many2one("product.brand", "Parent Brand")
    sequence = fields.Integer("Sequence", default=1)
    display_name = fields.Char("Dispaly Name", compute="_get_display_name", store=True)
    image = fields.Binary(
        attachment=True, help="This field holds the image used as image for the Brand, limited to 1024x1024px.")
    brand_count = fields.Integer("Total Product", compute="get_product_brand_count")
    visible_snippet = fields.Boolean("Visible in Snippet")
    product_ids = fields.One2many(
        'product.template',
        'brand_id',
        string='Product Brands',
    )
class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one("product.brand", "Brand")
    
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)
        product = self.env['product.product'].browse(combination_info['product_id']) or self
        combination_info.update(default_code=product.default_code)
        return combination_info

class ProductPerPageCountBizople(models.Model):
    _name = "product.per.page.count.bizople"
    _order = 'name asc'
    _description = "Add page no"

    name = fields.Integer(string='Product per page')
    default_active_count = fields.Boolean(string="Set default")
    prod_page_id = fields.Many2one('product.per.page.bizople')

    @api.model_create_multi
    def create(self, val_list):
        res = super(ProductPerPageCountBizople, self).create(val_list)
        for vals in val_list:
            if vals.get('name') == 0:
                raise Warning(
                    _("Warning! You cannot set 'zero' for product page."))
            if vals.get('default_active_count'):
                true_records = self.search(
                    [('default_active_count', '=', True), ('id', '!=', res.id)])
                true_records.write({'default_active_count': False})
        return res

    def write(self, vals):
        res = super(ProductPerPageCountBizople, self).write(vals)
        if vals.get('name') == 0:
            raise Warning(
                _("Warning! You cannot set 'zero' for product page."))
        if vals.get('default_active_count'):
            true_records = self.search(
                [('default_active_count', '=', True), ('id', '!=', self.id)])
            true_records.write({'default_active_count': False})
        return res

class ProductPerPageBizople(models.Model):
    _name = "product.per.page.bizople"
    _description = "Add no of product display in one page"

    name = fields.Char(string="Label Name", translate=True)
    prod_count_ids = fields.One2many(
        'product.per.page.count.bizople', 'prod_page_id', string="No of product to display")

    def write(self, vals):
        res = super(ProductPerPageBizople, self).write(vals)
        default_pg = self.env['product.per.page.count.bizople'].search(
            [('default_active_count', '=', True)])
        if default_pg.name:
            main.PPG = int(default_pg.name)
        else:
            raise Warning(
                _("Warning! You have to set atleast one default value."))
        return res

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    def get_product_category_count(self):
        for obj in self:
            categ_ids = [obj.id]
            sub_ids = [obj.id]
            while sub_ids:
                sub_ids = obj.env['product.public.category'].sudo().search([('parent_id', 'in', sub_ids)]).ids
                categ_ids = categ_ids + sub_ids
            domain = [('public_categ_ids', 'in', list(set(categ_ids)))]
            if not obj.env.user.has_group('base.group_system'):
                domain.append(("website_published", '=', True))
            ctx = obj.env.context or {}
            if 'product_categ_search' in ctx and ctx['product_categ_search']:
                domain.append(("name", 'ilike', ctx['product_categ_search'].strip()))
            product_template = self.env['product.template'].search(domain)
            obj.product_tmpl_count = len(product_template.ids)

    product_tmpl_count = fields.Integer(string="Total Product", compute="get_product_category_count")
    auto_assign = fields.Boolean("Auto Assign")
    quick_categ = fields.Boolean("Quick Category for Mobile", help='Categories visible on mobile view for Quick Search')
    category_bg_image = fields.Binary('Category Background Image', readonly=False)

    def get_all_parent_category(self):
        website = self.env['website'].get_current_website()
        domain = [('parent_id','=',False)] + website.website_domain()
        category = self.env['product.public.category'].search(domain)
        return category
        
class ProductPricelist(models.Model):
    _inherit = 'product.pricelist' 

    auto_assign = fields.Boolean("Auto Assign Category")

class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
    @api.model
    def add_auto_product_category(self):
        category_ids = self.env['product.public.category'].search([('auto_assign', '=', True)]).ids
        for obj in self:
            if obj.product_id:
                ecom_category_ids = obj.product_id.public_categ_ids.ids
                ecom_category_ids = list(set(ecom_category_ids + category_ids))
                obj.product_id.public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.product_tmpl_id:
                ecom_category_ids = obj.product_tmpl_id.public_categ_ids.ids
                ecom_category_ids = list(set(ecom_category_ids + category_ids))
                obj.product_tmpl_id.public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.categ_id:
                product_ids = self.env['product.product'].search([('categ_id', '=', obj.categ_id.id)])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = list(set(ecom_category_ids + category_ids))
                    product_id.public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.applied_on == '3_global':
                product_ids = self.env['product.product'].search([])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = list(set(ecom_category_ids + category_ids))
                    product_id.public_categ_ids = [[6, 0, ecom_category_ids]]
    
    @api.model
    def delete_auto_product_category(self):
        category_ids = self.env['product.public.category'].search([('auto_assign', '=', True)]).ids
        for obj in self:
            if obj.product_id:
                ecom_category_ids = obj.product_id.public_categ_ids.ids
                ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                obj.product_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.product_tmpl_id:
                ecom_category_ids = obj.product_tmpl_id.public_categ_ids.ids
                ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                obj.product_tmpl_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.categ_id:
                product_ids = self.env['product.product'].search([('categ_id', '=', obj.categ_id.id)])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                    product_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.applied_on == '3_global':
                product_ids = self.env['product.product'].search([])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                    product_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
    
    @api.model
    def get_update_category(self, pricelist_id):
        pricelist = False
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
        for obj in self:
            if not pricelist_id and obj.product_id.pricelist_id:
                pricelist = obj.product_id.pricelist_id
            elif not pricelist_id and obj.product_tmpl_id.pricelist_id:
                pricelist = obj.product_tmpl_id.pricelist_id
            if pricelist:
                if pricelist.auto_assign:
                    obj.add_auto_product_category()
                else:
                    obj.delete_auto_product_category()
    
    @api.model_create_multi
    def create(self, vals_list):
     for values in vals_list:
        res = super(ProductPricelistItem, self).create(values)
        if 'pricelist_id' in values and values['pricelist_id']:
            res.get_update_category(values['pricelist_id'])
        return res
    
    def write(self, vals):
        res = super(ProductPricelistItem, self).write(vals)
        if 'pricelist_id' in vals:
            for obj in self:
                obj.get_update_category(vals['pricelist_id'])
        elif 'product_id' in self:
            for obj in self:
                obj.get_update_category(obj.pricelist_id.id)
        elif 'product_tmpl_id' in vals:
            for obj in self:
                obj.get_update_category(obj.pricelist_id.id)
        return res

    @api.model
    def unlink(self):
        self.delete_auto_product_category()
        return super(ProductPricelistItem, self).unlink()

class BizBlogSlider(models.Model):
    _name = 'biz.blog.slider'
    _description = 'Blog Slider'

    name = fields.Char(string="Slider name", default='Blogs',
                       required=True, translate=True)
    active = fields.Boolean(string="Publish on Website", default=True)
    blog_subtitle = fields.Text(string="Slider sub title", help="""Slider sub title to be display""", translate=True)
    no_of_objects = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], string="Blogs Count",
                                    default='3',required=True)
    auto_slide = fields.Boolean(string='Auto Rotate Slider', default=True)
    sliding_speed = fields.Integer(string="Slider sliding speed", default='5000')
    blog_post_ids = fields.Many2many('blog.post', 'blogpost_slider_rel', 'slider_id',
                                             'post_id',
                                             string="Blogs", required=True, domain="[('is_published', '=', True)]")
