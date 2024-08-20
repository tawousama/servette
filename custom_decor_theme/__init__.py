# -*- coding: utf-8 -*-

from . import models
from . import controllers




def disable_products_tab_bizople(cr):
    cr.execute("""UPDATE ir_ui_view SET active=false WHERE key='theme_decor.decor_cart_popover'""")

def enable_products_tab_bizople(cr, registry):
    cr.execute("""UPDATE ir_ui_view SET active=true WHERE key='theme_decor.products_tab_bizople'""")