# -*- coding: utf-8 -*-
from . import models
def post_init_hook(cr, registry):
    cr.execute("""UPDATE ir_ui_view SET active=false WHERE key='theme_decor.decor_product_detail_inherited'""")
    