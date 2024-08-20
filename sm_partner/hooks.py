from odoo import SUPERUSER_ID, api


def post_init_hook(cr, _):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        partner_ids = env["res.partner"].sudo().search([])
        partner_ids._compute_name()
