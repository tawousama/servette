from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('res.city.zip')
        result.append('res.partner.category')
        return result

    def _loader_params_res_city_zip(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['id', 'name', 'display_name', 'state_id', 'city_id', 'country_id'],
            },
        }

    def _loader_params_res_partner_category(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['id', 'name', 'display_name', 'color'],
            },
        }

    def _get_pos_ui_res_city_zip(self, params):
        return self.env['res.city.zip'].search_read(**params['search_params'])

    def _get_pos_ui_res_partner_category(self, params):
        return self.env['res.partner.category'].search_read(**params['search_params'])

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()

        result['search_params']['fields'].extend(['zip_id', 'firstname', 'lastname', 'category_id'])
        return result
