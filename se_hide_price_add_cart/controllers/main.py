# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import werkzeug
import math

from odoo import http, tools, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class JistiMeet(http.Controller):
    @http.route('/meet/<int:id>/',type='http', auth="public", website=True)
    def jitsi_meet(self, id, **kwargs):
        record=request.env['jitsi.meet'].sudo().browse(id)
        if record:
            if not record.closed:
                data = {
                    'data': record,
                }
                return request.render("se_jitsi_meet.meet",data)
            else:
                return request.render("se_jitsi_meet.meet_closed")
        else:
            return request.render("se_jitsi_meet.meet_closed")