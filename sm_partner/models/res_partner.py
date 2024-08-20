from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends('firstname', 'lastname', 'type')
    def _compute_name(self):
        for record in self:
            lastname = record.lastname
            firstname = record.firstname
            if record.type == 'contact':
                if lastname:
                    lastname = lastname.upper()
                if firstname:
                    firstname = firstname.capitalize()
            record.name = record._get_computed_name(lastname, firstname)


    def _inverse_name_after_cleaning_whitespace(self):
        return False
