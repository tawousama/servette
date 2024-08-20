from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        if 'zip_id' in vals and vals['zip_id']:
            zip_id = self.env['res.city.zip'].sudo().browse(vals['zip_id'])
            vals['partner_latitude'] = zip_id.latitude
            vals['partner_longitude'] = zip_id.longitude

        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if 'zip_id' in vals and vals['zip_id']:
            zip_id = self.env['res.city.zip'].sudo().browse(vals['zip_id'])
            vals['partner_latitude'] = zip_id.latitude
            vals['partner_longitude'] = zip_id.longitude
        return super(ResPartner, self).write(vals)
