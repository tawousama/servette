from odoo import models, _


class ResConfigPrestashopInstance(models.TransientModel):
    _name = 'res.config.prestashop.instance'
    _description = 'Res Config Prestashop Instance'

    def not_done(self):
        """
        Discard the changes and reload the page.
        :return: Reload the page
        """
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
