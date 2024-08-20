# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64
from datetime import datetime
from io import BytesIO
from odoo.tools.safe_eval import safe_eval


class ProductTemplate(models.Model):
    _inherit = 'product.template'



    def _cron_out_of_stock_notification(self):
        products = self.search([('is_published', '=', True), ('qty_available', '<=', 0)])
        
      
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('produits en rupture de stock')
        
      
        headers = ['ID Externe', 'Nom', 'Stock', 'Video', 'Publié']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
       
        row = 1
        for product in products:
            sheet.write(row, 0, product.get_metadata()[0].get('xmlid') or '')  
            sheet.write(row, 1, product.name)  
            sheet.write(row, 2, product.qty_available) 
            sheet.write(row, 3, product.video if product.video else 'Non') 
            sheet.write(row, 4, 'Oui' if product.is_published else 'Non') 
            row += 1
        
        workbook.close()
        output.seek(0)
        
        excel_file = base64.b64encode(output.read())
        
        attachment = self.env['ir.attachment'].create({
            'name': f'Produits_en_rupture_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx',
            'datas': excel_file,
            'type': 'binary',
            'res_model': 'product.template',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        
        mail_template = self.env.ref('custom_decor_theme_2.mail_template_out_of_stock_notification')
        if mail_template:
            email_values = {
                 
                'attachment_ids': [(6, 0, [attachment.id])],
            }
            mail_template.send_mail(self.env.user.id, email_values=email_values, force_send=True)

        return True




