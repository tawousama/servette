# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, http
from odoo.http import request
import json

class PortalUser(http.Controller):
    @http.route(['/update-image'], type='json', auth="user")
    def action_update_image(self,**post):
        datas_file = str(post['img_attachment']).split(',')
        datas_file = datas_file[1]
        user_id = request.env.user
        datas_file = ''
        if 'img_attachment' in post and post['img_attachment']:
            datas_file = str(post['img_attachment']).split(',')
            datas_file = datas_file[1]
            user_id.write({'image_1920':datas_file})
        values = {'user_id':user_id}
        return request.env['ir.ui.view']._render_template("theme_decor.update_user_image",values)
 
class PortalAddress(http.Controller):
	
	@http.route(['/get-related-state'], type='json', auth="public")
	def get_related_state(self, **post):
		state_vals = """<option value="">State / Province...</option>"""+','
		state_ids = False
		if post['country_id']:
			state_ids = request.env['res.country.state'].sudo().search([('country_id','=',int(post['country_id']))])
			for state in state_ids:
				state_vals += """<option t-att-value="""+'"'+str(state.id)+'"'+""">"""+state.name+"""</option>"""+','
		return {'state_ids':len(state_ids),'state_vals':state_vals}

	@http.route(['/my-address'], type='http', auth="public", website=True, sitemap=False)
	def partner_address(self,**post):
		partner_id = request.env.user.partner_id
		values = {}
		countries = request.env['res.country'].sudo().search([])
		if countries:
			countries = countries[0].get_website_sale_countries()
		shippings = partner_id.search([('id', 'child_of', partner_id.commercial_partner_id.ids),('is_removed','!=',True)])
		values = {'countries':countries,'shippings':shippings,'billing':partner_id,'shipping_count':len(shippings)}
		return request.render('theme_decor.address_list',values)

	@http.route(['/update-addres/<model("res.partner"):partner>'], type='http', auth="public", website=True, sitemap=False)
	def update_shipping_addres(self,partner,**post):
		partner_id = request.env.user.partner_id
		shipping_partner_id = request.env['res.partner'].sudo().browse(int(partner))
		if shipping_partner_id:
			partner_id.sudo().write({'default_shipping_id':shipping_partner_id.id})
		return request.redirect("/my-address")

	@http.route(['/delete-address/<model("res.partner"):partner>'], type='http', auth="public", website=True, sitemap=False)
	def delete_shipping_addres(self,partner,**post):
		partner_id = request.env.user.partner_id
		shipping_partner_id = request.env['res.partner'].sudo().browse(int(partner))
		if shipping_partner_id:
			shipping_partner_id.is_removed = True
		return request.redirect("/my-address")

	@http.route(['/add-address'], type='http', auth="public", website=True, sitemap=False)
	def add_new_address(self,**post):
		required_fields = []
		predefine_data = {}
		user_id = request.env.user
		company_id = user_id.company_id
		values = {}
		partner_id = False
		error_message = ""
		if 'data' in post and post['data']:
			predefine_data = json.loads(post['data'].replace("'", '"'))
		if 'error' in post and post['error']:
			required_fields = post['error'].strip().split(',')
			error_message = "Update required fields!"		
		countries = request.env['res.country'].sudo().search([])
		state_ids = request.env['res.country.state'].sudo().search([])
		if 'edit-mode' in  post and post['edit-mode']:
			partner_id = request.env['res.partner'].sudo().browse(int(post['edit-mode']))
			values.update({
				'mode':'edit-mode',		
			})
		elif 'new-address' in post and post['new-address']:
			values.update({
				'mode':'new-address',		
			})
		if 'submitted' in post and post['submitted']:
			required_fields = ['name','city','street','phone']
			values = {}
			update_partner_id = False
			rfields = []
			if 'partner_id' in post and post['partner_id']:
				partner = ''.join(x for x in post['partner_id'] if x.isdigit())
				update_partner_id = request.env['res.partner'].sudo().browse(int(partner))
			error_message = ''
			for require_field in required_fields:
				if require_field in post and not post[require_field]:
					rfields.append(require_field)
			if rfields:
				error_message = ','.join(rfields)
			if  error_message:		
				return request.redirect("/add-address?data=%s&error=%s" % (post, error_message))
			partner_id = request.env.user.partner_id
			partner_vals = {}
			if 'name' in post and post['name']:
				partner_vals.update({'name':post['name']})
			if 'email' in post and post['email']:
				partner_vals.update({'email':post['email']})
			if 'phone' in post and post['phone']:
				partner_vals.update({'phone':post['phone']})
			if 'street' in post and post['street']:
				partner_vals.update({'street':post['street']})
			if 'street2' in post and post['street2']:
				partner_vals.update({'street2':post['street2']})
			if 'zip' in post and post['zip']:
				partner_vals.update({'zip':post['zip']})
			if 'city' in post and post['city']:
				partner_vals.update({'city':post['city']})

			if 'state_id' in post and post['state_id']:
				state_id = request.env['res.country.state'].sudo().search([('name','=',post['state_id'])])
				partner_vals.update({'state_id': state_id.id})
			if 'country_id' in post and post['country_id']:
				partner_vals.update({'country_id':int(post['country_id'])})
			if 'mode' in  post and post['mode']:
				if post['mode'] == 'edit-mode' and update_partner_id:
					delivery_partner_id = update_partner_id.sudo().write(partner_vals)
				elif post['mode'] == 'new-address':
					partner_vals.update({'parent_id':partner_id.id,'type':'delivery'})
					delivery_partner_id = request.env['res.partner'].sudo().create(partner_vals)
			return request.redirect('/my-address')
		else:
			values.update({
				'partner_id':partner_id,
				'required_fields':required_fields,
				'error_message':error_message,
				'countries':countries,
				'predefine_data':predefine_data,
				'state_ids':state_ids,			
			})
		return request.render('theme_decor.add_address',values)