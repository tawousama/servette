# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from odoo import api, models, fields


class TemplateMailing(models.Model):
    _name = 'template.mailing'
    _description = 'Template Mailing'

    name = fields.Char(string='Name',
                       required=True)
    template_text = fields.Html(string='Template Text')


class MassMailing(models.Model):
    _inherit = "mailing.mailing"

    template_mailing_id = fields.Many2one('template.mailing',
                                          string='Mail Template')

    @api.onchange('template_mailing_id')
    def onchange_template_mailing(self):
        self.body_arch = self.template_mailing_id.template_text

    def button_save_template(self):
        template_mailing_id = self.env['template.mailing'].create(
            {'template_text': self.body_arch,
             'name': "New Template"})
        self.template_mailing_id = template_mailing_id.id
