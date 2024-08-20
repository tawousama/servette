# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.product'

    video = fields.Char("Video")
    spec_technique = fields.Html("Spécifications Téchniques", translate=True )

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    video = fields.Char("Video")
    spec_technique = fields.Html("Spécifications Téchniques", translate=True)
    description_courte = fields.Char("Déscription Courte", translate=True)


class ProductPublicCategoryInherit(models.Model):
    _inherit = "product.public.category"


    def get_categories_to_show(self):
        categs = False
        if self.parent_id:
            categs = self.parent_id
            if self.parent_id.child_id:
                 categs = categs - self.parent_id.child_id
        else:
            categs = self
        return categs


class CrmLead(models.Model):
    _inherit = "crm.lead"

    produits = fields.Many2many("product.template", string="Produits")
  
    