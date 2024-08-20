odoo.define('theme_decor.popoverCart', function (require) {
'use strict';

	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var _t = core._t;
	var timeout;

	publicWidget.registry.websiteSaleCartLink.include({
	    selector: '.bizople-add-to-cart a[href$="/shop/cart"], #top_menu a[href$="/shop/cart"], .o_wsale_my_cart a[href$="/shop/cart"]',
	});
});