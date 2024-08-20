from odoo import api, fields, models, _
import base64, urllib
from io import BytesIO
import requests, base64, sys
import os
import logging

logger = logging.getLogger('__name__')


# TODO find a good solution in order to roll back changed done on file system
# TODO add the posibility to move from a store system to an other (example : moving existing image on database to file system)

class GtPrestashopProductImages(models.Model):
    "Products Image gallery"
    _name = "gt.prestashop.product.images"
    _description = 'Prestashop Product Images'

    @api.model
    def unlink(self):
        local_media_repository = self.env['res.company'].get_local_media_repository()
        if local_media_repository:
            for image in self:
                path = os.path.join(local_media_repository, image.product_id.default_code, image.name)
                if os.path.isfile(path):
                    os.remove(path)
        return super(GtPrestashopProductImages, self).unlink()

    # @api.model
    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name', False) and not val.get('extention', False):
                val['name'], val['extention'] = os.path.splitext(val['name'])
        return super(GtPrestashopProductImages, self).create(vals)

    def write(self, vals):
        if vals.get('name', False) and not vals.get('extention', False):
            vals['name'], vals['extention'] = os.path.splitext(vals['name'])
        if vals.get('name', False) or vals.get('extention', False):
            local_media_repository = self.env['res.company'].get_local_media_repository()
            if local_media_repository:
                #                 old_images = self.browse(cr, uid, ids, context=context)
                res = []
                for old_image in self:
                    if vals.get('name', False) and (old_image.name != vals['name']) or vals.get('extention',
                                                                                                False) and (
                            old_image.extention != vals['extention']):
                        old_path = os.path.join(local_media_repository, old_image.product_id.default_code,
                                                '%s%s' % (old_image.name, old_image.extention))
                        res.append(super(GtPrestashopProductImages, self).write(old_image.id, vals))
                        if 'file' in vals:
                            # a new image have been loaded we should remove the old image
                            # TODO it's look like there is something wrong with function field in openerp indeed the preview is always added in the write :(
                            if os.path.isfile(old_path):
                                os.remove(old_path)
                        else:
                            # we have to rename the image on the file system
                            if os.path.isfile(old_path):
                                os.rename(old_path,
                                          os.path.join(local_media_repository, old_image.product_id.default_code,
                                                       '%s%s' % (old_image.name, old_image.extention)))
                return res
        if 'file_db_store' in vals:
            vals["image_to_update"] = True
            vals["image"] = vals['file_db_store']

        return super(GtPrestashopProductImages, self).write(vals)

    def get_image(self):
        product_product_obj = self.env['product.product']
        product_template_obj = self.env['product.template']
        for rec in self:
            print('----------------test1111---------', rec)
            # each = rec.sudo().read(['link', 'url', 'name', 'file_db_store', 'product_id', 'product_t_id', 'name', 'extention'])[0]
            print('----------------test22222---------')
            # if each['link']:
            if rec.link:
                # filename = BytesIO(requests.get(each['url']).content)
                filename = BytesIO(requests.get(rec.url).content)
                img = base64.b64encode(filename.getvalue())

                # (filename, header) = urllib.request.urlretrieve(each['url'])
                # f = open(filename , 'rb')
                # img = base64.encodestring(f.read())
                # f.close()
                rec.file = img
            else:
                local_media_repository = self.env['res.company'].get_local_media_repository()
                if local_media_repository:
                    # if each['product_t_id']:
                    if rec.product_t_id:
                        # product_id = product_template_obj.browse(rec.product_t_id[0])
                        # product_id = product_template_obj.browse(each['product_t_id'][0])
                        # product_id = product_template_obj.browse(each['product_t_id'][0])
                        # product_code = product_id.read(['default_code'])[0]['default_code']
                        product_code = rec.product_t_id.default_code
                    else:
                        # product_id = product_product_obj.browse(each['product_id'][0])
                        # product_code = product_id.read(['default_code'])[0]['default_code']
                        product_code = rec.product_id.default_code
                    # full_path = os.path.join(local_media_repository, product_code, '%s%s'%(each['name'], each['extention']))
                    print('product_code----------', product_code)
                    full_path = os.path.join(local_media_repository, product_code, '%s%s' % (rec.name, rec.extention))
                    print('full_path-------', full_path)
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'rb') as image:
                                img = image.read().encode("base64")
                            # f.close()
                        except Exception as e:
                            return False
                    else:
                        return False
                else:
                    img = rec.file_db_store
                    # img = each['file_db_store']
                    rec.file = img

    def _get_image(self):
        res = {}
        for each in self:
            res[each] = self.get_image()
        return res

    def _check_filestore(self, image_filestore):
        '''check if the filestore is created, if not it create it automatically'''
        #         try:
        if not os.path.isdir(image_filestore):
            os.makedirs(image_filestore)
        #         except Exception e:
        #             raise osv.except_osv(_('Error'), _('The image filestore can not be created, %s'%e))
        return True

    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        full_path = os.path.join(path, filename)
        self._check_filestore(path)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.b64decode(b64_file))
        finally:
            ofile.close()
        return True

    #Error fixing 15-11-2023
    # def _set_image(self, name, value, arg):
    def _set_image(self):
        logger.info("self %s" % (self))
        local_media_repository = self.env['res.company'].get_local_media_repository()
        if local_media_repository:
            logger.info("enter this condition")
            #             image = self.browse(cr, uid, id, context=context)
            return self._save_file(os.path.join(local_media_repository, self.product_id.default_code),
                                   '%s%s' % (self.name, self.extention), self.file)
        return self.write({'file_db_store': self.file}) if self.file else False
        # return self.write({'file_db_store': value})

    name = fields.Char('Image Title', size=100, required=True)
    extention = fields.Char('file extention', size=6)
    link = fields.Boolean('Link?', default=lambda *a: False,
                          help="Images can be linked from files on your file system or remote (Preferred)")
    file_db_store = fields.Binary('Image stored in database')
    # file = fields.Char(compute=_get_image, inverse=_set_image, type="binary")
    file = fields.Char(compute=_get_image, type="binary")
    url = fields.Char('File Location', size=250)
    comments = fields.Text('Comments')
    product_id = fields.Many2one('product.product', 'Product')
    product_t_id = fields.Many2one('product.template', 'Product Images')
    image_url = fields.Char('Image URL')
    image = fields.Binary('Image')
    prest_img_id = fields.Integer('Img ID')
    is_default_img = fields.Boolean('Default')
    prest_product_id = fields.Integer('Presta Product ID')
    shop_ids = fields.Many2many('prestashop.shop', 'img_shop_rel', 'img_id', 'shop_id', string="Shop")
    write_date = fields.Datetime(string="Write Date")
    image_to_update = fields.Boolean('image to upd on prestashop', default=False)

    _sql_constraints = [('uniq_name_product_id', 'UNIQUE(product_id, name)',
                         _('A product can have only one image with the same name'))]


