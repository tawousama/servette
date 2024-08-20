from odoo import api, fields, models


class product_template(models.Model):
    _inherit = 'product.template'

    website_description = fields.Html('Description Site web', translate=True)
    summary = fields.Html(translate=True, sanitize=False)
    sp_eacute_specifications_techniques = fields.Html('Technical Specifications', translate=True, sanitize=False)
