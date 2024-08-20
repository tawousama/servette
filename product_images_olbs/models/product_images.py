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
# import urllib.request
from odoo import api, fields, models, _
import base64, urllib
from io import BytesIO
import requests, base64, sys
import os
import odoo.netsvc


# TODO find a good solution in order to roll back changed done on file system
# TODO add the posibility to move from a store system to an other (example : moving existing image on database to file system)


class product_images(models.Model):
    "Products Image gallery"
    _name = "product.images"
    _description = __doc__

    @api.model
    def unlink(self):
        local_media_repository = self.env['res.company'].get_local_media_repository()
        if local_media_repository:
            for image in self:
                path = os.path.join(local_media_repository, image.product_id.default_code, image.name)
                if os.path.isfile(path):
                    os.remove(path)
        return super(product_images, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', False) and not vals.get('extention', False):
            vals['name'], vals['extention'] = os.path.splitext(vals['name'])
        return super(product_images, self).create(vals)

    def write(self, vals):
        if vals.get('name', False) and not vals.get('extention', False):
            vals['name'], vals['extention'] = os.path.splitext(vals['name'])
        if vals.get('name', False) or vals.get('extention', False):
            local_media_repository = self.env['res.company'].get_local_media_repository()
            if local_media_repository:
                #                 old_images = self.browse(cr, uid, ids, context=context)
                res = []
                for old_image in self:
                    if vals.get('name', False) and (old_image.name != vals['name']) or vals.get('extention', False) and (old_image.extention != vals['extention']):
                        old_path = os.path.join(local_media_repository, old_image.product_id.default_code, '%s%s' % (old_image.name, old_image.extention))
                        res.append(super(product_images, self).write(old_image.id, vals))
                        if 'file' in vals:
                            # a new image have been loaded we should remove the old image
                            # TODO it's look like there is something wrong with function field in openerp indeed the preview is always added in the write :(
                            if os.path.isfile(old_path):
                                os.remove(old_path)
                        else:
                            # we have to rename the image on the file system
                            if os.path.isfile(old_path):
                                os.rename(old_path, os.path.join(local_media_repository, old_image.product_id.default_code, '%s%s' % (old_image.name, old_image.extention)))
                return res
        return super(product_images, self).write(vals)

    def get_image(self):
        for rec in self:
            if rec.link:
                filename = BytesIO(requests.get(rec.url).content)
                img = base64.b64encode(filename.getvalue())
                rec.file = img
            else:
                local_media_repository = self.env['res.company'].get_local_media_repository()
                if local_media_repository:
                    if rec.product_t_id:
                        product_code = rec.product_t_id.default_code
                    else:
                        product_code = rec.product_id.default_code
                    full_path = os.path.join(local_media_repository, product_code, '%s%s' % (rec.name, rec.extention))
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'rb') as image:
                                img = image.read().encode("base64")
                        except Exception as e:
                            return False
                    else:
                        return False

    def _get_image(self):
        res = {}
        for each in self:
            res[each] = self.get_image()
        return res

    def _check_filestore(self, image_filestore):
        '''check if the filestore is created, if not it create it automatically'''
        if not os.path.isdir(image_filestore):
            os.makedirs(image_filestore)
        return True

    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        full_path = os.path.join(path, filename)
        self._check_filestore(path)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True

    def _set_image(self, name, value, arg):
        local_media_repository = self.env['res.company'].get_local_media_repository()
        if local_media_repository:
            return self._save_file(os.path.join(local_media_repository, self.product_id.default_code), '%s%s' % (self.name, self.extention), value)
        return self.write({'file_db_store': value})

    name = fields.Char('Image Title', size=100, required=True)
    extention = fields.Char('file extention', size=6)
    link = fields.Boolean('Link?', default=lambda *a: False, help="Images can be linked from files on your file system or remote (Preferred)")
    file_db_store = fields.Binary('Image stored in database')
    file = fields.Char(compute=_get_image, inverse=_set_image, type="binary")
    url = fields.Char('File Location', size=250)
    comments = fields.Text('Comments')
    product_id = fields.Many2one('product.product', 'Product')
    product_t_id = fields.Many2one('product.template', 'Product Images', ondelete='cascade')

    _sql_constraints = [('uniq_name_product_id', 'UNIQUE(product_id, name)',
                         _('A product can have only one image with the same name'))]
