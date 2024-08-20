from odoo import models, fields, api


class ResCityZip(models.Model):
    _inherit = 'res.city.zip'

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    latitude = fields.Float('Latitude – N', digits=(10, 7))
    longitude = fields.Float('Longitude – E', digits=(10, 7))
    additional_digit = fields.Char(
        string='Chiffre supplémentaire',
    )
    lang_id = fields.Many2one('res.lang',
                              string='Langue'
                              )

    communitynumber_bfs = fields.Integer(
        string='BFS-Nr',
        help="Numbering used by the Federal Statistical Office for "
             "municipalities in Switzerland and the Principality of "
             "Liechtenstein",
    )
    commune_name = fields.Char('Nom de la commune')

    display_name = fields.Char(
        compute="_compute_new_display_name",
        search='search_new_display_name',
        store=False,
        index=True
    )

    @api.depends("name", "city_id", "city_id.state_id", "city_id.country_id")
    def _compute_new_display_name(self):
        for rec in self:
            name = [rec.name, rec.city_id.name]
            if rec.city_id.state_id:
                name.append(rec.city_id.state_id.name)
            if rec.city_id.country_id:
                name.append(rec.city_id.country_id.with_context(lang=self.env.lang).name)
            rec.display_name = ", ".join(name)

    def search_new_display_name(self, operator, value):
        zip_ids = self.env['res.city.zip'].sudo().search(['|', '|', '|',
                                                          ('name', operator, value),
                                                          ('city_id.name', operator, value),
                                                          ('state_id.name', operator, value),
                                                          ('country_id.name', operator, value),
                                                          ])
        return [('id', 'in', zip_ids.ids)]
