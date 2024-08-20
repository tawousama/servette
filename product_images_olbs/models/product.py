# -*- encoding: utf-8 -*-
#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
# Copyright (C) 2011 Akretion Sébastien BEAU sebastien.beau@akretion.com#
#                                                                       #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                       #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                       #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
from odoo import api, fields, models, _
import os


class product_product(models.Model):
    _inherit = "product.product"

    @api.model
    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'default_code': False,
            'images_ids': False,
        })
        return super(product_product, self).copy(default)

    def get_main_image(self):
        images_ids = self.read(['image_ids'])['image_ids']
        if images_ids:
            return images_ids[0]
        return False
    
    def _get_main_image(self, field_name, arg):
        res = {}
        img_obj = self.env['product.images']
        for id in self:
            image_id = self.get_main_image()
            if image_id:
                image = img_obj.browse(image_id)
                res[id] = image.file
            else:
                res[id] = False
        return res

    image_ids = fields.One2many(
            'product.images',
            'product_id',
            'Product Images'
    )
    product_image = fields.Char(compute='_get_main_image', type="binary")
    
    def write(self, vals):
        # here we expect that the write on default_code is alwayse on 1 product because there is an unique constraint on the default code
        if vals.get('default_code', False) and self:
            local_media_repository = self.env['res.company'].get_local_media_repository()
            if local_media_repository:
                old_product = self.read(['default_code', 'image_ids'])
                res = super(product_product, self).write(vals)
                # if old_product['image_ids']:
                #    if old_product['default_code'] != vals['default_code']:
                #        old_path = os.path.join(local_media_repository, old_product['default_code'])
                #        if os.path.isdir(old_path):
                #            os.rename(old_path,  os.path.join(local_media_repository, vals['default_code']))
                return res
        return super(product_product, self).write(vals)
